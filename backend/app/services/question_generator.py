"""
Main orchestrator for exam question generation.

Flow:
  1. Load exam config from DB
  2. Load syllabus topics
  3. Calculate question distribution → list of batch specs
  4. For each batch: call LLM → parse → validate → collect
  5. Store valid questions in question_bank
  6. Assemble 65-question exam
  7. Update exam row with question_ids, question_order, status
"""

import asyncio
import json
import logging
import math
import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.core.llm_config import (
    GA_1MARK,
    GA_2MARK,
    SUBJECT_1MARK,
    SUBJECT_2MARK,
    GATE_TOTAL_QUESTIONS,
)
from app.models.exam import Exam
from app.models.syllabus import Syllabus
from app.models.question_bank import QuestionBank
from app.services.llm_service import call_llm, extract_json_array
from app.services.question_validator import validate_batch
from app.services.exam_assembler import assemble_exam, compute_marks_summary

logger = logging.getLogger(__name__)

# ── Load prompt templates ──
PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

def _load_prompt(filename: str) -> dict:
    filepath = PROMPTS_DIR / filename
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

_BATCH_PROMPT = _load_prompt("generate_batch.json")
_GA_PROMPT = _load_prompt("generate_ga.json")

PAPER_NAMES = {
    "CS": "Computer Science and Information Technology",
    "DA": "Data Science and Artificial Intelligence",
}


# ──────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────

async def run_generation(exam_id: uuid.UUID) -> None:
    """
    Background task: generates all questions for an exam.
    Uses its own DB session (not the request session).
    """
    async with AsyncSessionLocal() as db:
        try:
            await _do_generation(db, exam_id)
        except Exception as exc:
            logger.exception(f"Exam generation failed for {exam_id}: {exc}")
            await _set_error(db, exam_id, str(exc))


async def _do_generation(db: AsyncSession, exam_id: uuid.UUID) -> None:
    # ── 1. Load exam config ──
    exam = await db.get(Exam, exam_id)
    if exam is None:
        raise ValueError(f"Exam {exam_id} not found")

    logger.info(f"Starting generation for exam {exam_id} (paper={exam.paper})")

    # ── 2. Load syllabus topics ──
    subject_sections = await _load_syllabus_grouped(db, exam.paper)
    ga_sections = await _load_syllabus_grouped(db, "GA")

    if not subject_sections:
        raise ValueError(f"No syllabus data for paper {exam.paper}")
    if not ga_sections:
        raise ValueError("No syllabus data for GA")

    # Filter subject sections if scope is 'topic'
    if exam.scope == "topic" and exam.selected_topics:
        selected = set(exam.selected_topics)
        filtered = {}
        for sec_name, topics in subject_sections.items():
            matching = [t for t in topics if t in selected]
            if matching:
                filtered[sec_name] = matching
        if not filtered:
            raise ValueError("No matching sections for selected topics")
        subject_sections = filtered

    # ── 3. Build batch plan ──
    types_ratio = exam.types_ratio or {"MCQ": 0.6, "MSQ": 0.2, "NAT": 0.2}
    difficulty = exam.difficulty

    batches = _build_batch_plan(
        subject_sections=subject_sections,
        ga_sections=ga_sections,
        types_ratio=types_ratio,
        difficulty=difficulty,
        paper=exam.paper,
    )

    total_expected = sum(b["count"] for b in batches)
    logger.info(f"Batch plan: {len(batches)} batches, {total_expected} questions expected")

    # ── 4. Generate questions batch by batch ──
    all_questions: list[dict] = []
    completed = 0
    failed = 0

    for batch_idx, batch_spec in enumerate(batches):
        try:
            raw = await _generate_one_batch(batch_spec)
            valid = validate_batch(raw, expected_section=batch_spec["section_name"])

            # Tag each question with paper
            for q in valid:
                q["_paper"] = exam.paper if batch_spec["is_ga"] is False else "GA"

            all_questions.extend(valid)
            completed += len(valid)
            failed += batch_spec["count"] - len(valid)

            logger.info(
                f"Batch {batch_idx + 1}/{len(batches)}: "
                f"{len(valid)}/{batch_spec['count']} valid"
            )

        except Exception as exc:
            logger.error(f"Batch {batch_idx + 1} failed entirely: {exc}")
            failed += batch_spec["count"]

        # Update progress
        exam.generation_progress = {
            "total": GATE_TOTAL_QUESTIONS,
            "completed": min(completed, GATE_TOTAL_QUESTIONS),
            "failed": failed,
            "batch": f"{batch_idx + 1}/{len(batches)}",
        }
        await db.commit()

    logger.info(
        f"Generation done: {len(all_questions)} valid questions "
        f"({completed} completed, {failed} failed)"
    )

    if len(all_questions) < 20:
        raise ValueError(
            f"Only generated {len(all_questions)} valid questions — "
            "not enough to assemble an exam. Check LLM configuration."
        )

    # ── 5. Store questions in question_bank ──
    stored_ids = await _store_questions(db, all_questions, exam)

    # ── 6. Assemble exam ──
    question_order, selected = assemble_exam(all_questions, exam.paper)

    # Map question_order IDs to stored UUIDs
    for i, entry in enumerate(question_order):
        if i < len(stored_ids):
            entry["question_id"] = str(stored_ids[i])

    summary = compute_marks_summary(question_order)
    logger.info(f"Exam assembled: {summary}")

    # ── 7. Update exam row ──
    exam.question_ids = [str(qid) for qid in stored_ids[: len(selected)]]
    exam.question_order = question_order
    exam.status = "generated"
    exam.generation_progress = {
        "total": GATE_TOTAL_QUESTIONS,
        "completed": len(question_order),
        "failed": 0,
    }
    await db.commit()

    logger.info(f"Exam {exam_id} generation complete — status: generated")


# ──────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────

async def _load_syllabus_grouped(
    db: AsyncSession, paper: str
) -> dict[str, list[str]]:
    """Load syllabus topics grouped by section_name."""
    result = await db.execute(
        select(Syllabus.section_name, Syllabus.topic)
        .where(Syllabus.paper == paper)
        .order_by(Syllabus.section_name, Syllabus.id)
    )
    rows = result.fetchall()

    grouped: dict[str, list[str]] = {}
    for section_name, topic in rows:
        grouped.setdefault(section_name, []).append(topic)
    return grouped


def _build_batch_plan(
    subject_sections: dict[str, list[str]],
    ga_sections: dict[str, list[str]],
    types_ratio: dict[str, float],
    difficulty: str,
    paper: str,
) -> list[dict]:
    """
    Create a list of batch specifications.
    Each batch = one LLM call producing up to 5 questions.
    """
    batches: list[dict] = []

    # ── GA batches ──
    all_ga_topics = []
    for topics in ga_sections.values():
        all_ga_topics.extend(topics)

    batches.append({
        "section_name": "General Aptitude",
        "paper": paper,
        "is_ga": True,
        "topics": all_ga_topics,
        "marks": 1,
        "count": GA_1MARK,
        "types": {"MCQ": GA_1MARK},
        "difficulty": difficulty if difficulty != "auto" else "easy",
    })
    batches.append({
        "section_name": "General Aptitude",
        "paper": paper,
        "is_ga": True,
        "topics": all_ga_topics,
        "marks": 2,
        "count": GA_2MARK,
        "types": {"MCQ": GA_2MARK},
        "difficulty": difficulty if difficulty != "auto" else "medium",
    })

    # ── Subject batches ──
    num_sections = len(subject_sections)
    if num_sections == 0:
        return batches

    # Distribute 55 questions across sections
    base = SUBJECT_1MARK + SUBJECT_2MARK  # 55
    per_section = base // num_sections
    remainder = base % num_sections

    section_list = list(subject_sections.items())

    # Distribute 1-mark and 2-mark across sections
    remaining_1m = SUBJECT_1MARK  # 25
    remaining_2m = SUBJECT_2MARK  # 30

    for i, (sec_name, topics) in enumerate(section_list):
        total_for_section = per_section + (1 if i < remainder else 0)

        # Split into 1-mark and 2-mark proportionally
        sec_1m = round(total_for_section * SUBJECT_1MARK / base)
        sec_2m = total_for_section - sec_1m

        # Clamp to remaining
        sec_1m = min(sec_1m, remaining_1m)
        sec_2m = min(sec_2m, remaining_2m)

        # If we under-allocated, adjust
        if sec_1m + sec_2m < total_for_section:
            diff = total_for_section - sec_1m - sec_2m
            if remaining_1m - sec_1m >= diff:
                sec_1m += diff
            else:
                sec_2m += diff

        remaining_1m -= sec_1m
        remaining_2m -= sec_2m

        # Determine types for this section's questions
        for marks_val, count in [(1, sec_1m), (2, sec_2m)]:
            if count == 0:
                continue

            types_dist = _distribute_types(count, types_ratio)
            diff_level = _pick_difficulty(difficulty, marks_val)

            # Split into batches of max 5
            specs_for_batch = _build_question_specs(types_dist, marks_val)

            for chunk_start in range(0, len(specs_for_batch), 5):
                chunk = specs_for_batch[chunk_start : chunk_start + 5]
                type_counts: dict[str, int] = {}
                for s in chunk:
                    type_counts[s] = type_counts.get(s, 0) + 1

                batches.append({
                    "section_name": sec_name,
                    "paper": paper,
                    "is_ga": False,
                    "topics": topics,
                    "marks": marks_val,
                    "count": len(chunk),
                    "types": type_counts,
                    "difficulty": diff_level,
                })

    return batches


def _distribute_types(count: int, ratio: dict[str, float]) -> dict[str, int]:
    """Distribute `count` questions across MCQ/MSQ/NAT based on ratio."""
    mcq = round(count * ratio.get("MCQ", 0.6))
    msq = round(count * ratio.get("MSQ", 0.2))
    nat = count - mcq - msq  # remainder goes to NAT

    # Ensure no negatives
    if nat < 0:
        nat = 0
        msq = count - mcq

    return {"MCQ": mcq, "MSQ": msq, "NAT": nat}


def _build_question_specs(types_dist: dict[str, int], marks: int) -> list[str]:
    """Build a flat list of type strings, e.g., ['MCQ', 'MCQ', 'MSQ', 'NAT']."""
    specs: list[str] = []
    for qtype, count in types_dist.items():
        specs.extend([qtype] * count)
    return specs


def _pick_difficulty(difficulty: str, marks: int) -> str:
    """Pick difficulty for a batch."""
    if difficulty != "auto":
        return difficulty
    # Auto: 1-mark tends easier, 2-mark tends harder
    return "medium" if marks == 1 else "hard"


async def _generate_one_batch(batch_spec: dict) -> list[dict]:
    """Generate one batch of questions via LLM."""
    is_ga = batch_spec["is_ga"]
    prompt_template = _GA_PROMPT if is_ga else _BATCH_PROMPT

    # Build the question specs text
    specs_lines = []
    idx = 1
    for qtype, count in batch_spec["types"].items():
        for _ in range(count):
            specs_lines.append(f"{idx}. {qtype}, {batch_spec['marks']} mark(s)")
            idx += 1

    question_specs = "\n".join(specs_lines)

    # Build topics list
    topics_list = "\n".join(f"- {t}" for t in batch_spec["topics"])

    # Format user prompt
    if is_ga:
        user_prompt = prompt_template["user_prompt_template"].format(
            count=batch_spec["count"],
            marks=batch_spec["marks"],
            difficulty=batch_spec["difficulty"],
            topics_list=topics_list,
        )
    else:
        user_prompt = prompt_template["user_prompt_template"].format(
            count=batch_spec["count"],
            paper=batch_spec["paper"],
            paper_full_name=PAPER_NAMES.get(batch_spec["paper"], batch_spec["paper"]),
            section_name=batch_spec["section_name"],
            difficulty=batch_spec["difficulty"],
            question_specs=question_specs,
            topics_list=topics_list,
        )

    system_prompt = prompt_template["system_prompt"]

    # Call LLM
    raw_response = await call_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=settings.LLM_TEMPERATURE,
    )

    # Parse JSON
    questions = extract_json_array(raw_response)

    # Ensure section_name is set correctly
    for q in questions:
        if is_ga:
            q["section_name"] = "General Aptitude"
        elif not q.get("section_name"):
            q["section_name"] = batch_spec["section_name"]

    return questions


async def _store_questions(
    db: AsyncSession,
    questions: list[dict],
    exam: Exam,
) -> list[uuid.UUID]:
    """Store generated questions in the question_bank table."""
    stored_ids: list[uuid.UUID] = []

    for q in questions:
        qb = QuestionBank(
            id=uuid.uuid4(),
            paper=exam.paper if q.get("section_name") != "General Aptitude" else "GA",
            question_type=q["question_type"],
            marks=q["marks"],
            difficulty=q.get("difficulty", "medium"),
            difficulty_score=q.get("difficulty_score", 0.5),
            section_name=q["section_name"],
            topic=q.get("topic", "General"),
            stem_tex=q["stem_tex"],
            code_snippet=q.get("code_snippet"),
            code_language=q.get("code_language"),
            choices=q.get("choices"),
            answer=q["answer"],
            solution_tex=q["solution_tex"],
            estimated_time_seconds=q.get("estimated_time_seconds"),
            llm_model=settings.NEBIUS_MODEL,
            llm_prompt_version="1.0",
            validated=True,
        )
        db.add(qb)
        stored_ids.append(qb.id)

    await db.flush()
    return stored_ids


async def _set_error(db: AsyncSession, exam_id: uuid.UUID, error_msg: str) -> None:
    """Mark an exam generation as failed."""
    exam = await db.get(Exam, exam_id)
    if exam:
        exam.status = "failed"
        exam.generation_progress = {
            **(exam.generation_progress or {}),
            "error": error_msg,
        }
        await db.commit()