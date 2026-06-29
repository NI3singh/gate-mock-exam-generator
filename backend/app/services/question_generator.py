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
from app.services.llm_service import (
    call_llm,
    extract_json_array,
    get_active_llm_metadata,
)
from app.services.question_validator import (
    question_slots_from_batch,
    slot_spec_from_batch,
    validate_batch_aligned,
)
from app.services.tex_sanitize import sanitize_question_fields
from app.services.exam_assembler import assemble_exam, compute_marks_summary
from app.services.question_verifier import verify_questions
from app.services.pyq_retrieval import retrieve_exemplars, format_exemplars

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

    grounding_on = settings.PYQ_GROUNDING_ENABLED and bool(exam.use_pyq_reference)
    if grounding_on:
        logger.info("PYQ grounding is ON for this generation")

    # ── 4. Generate questions batch by batch ──
    all_questions: list[dict] = []
    deficit_slots: list[dict] = []
    completed = 0

    for batch_idx, batch_spec in enumerate(batches):
        try:
            await _attach_exemplars(db, batch_spec, enabled=grounding_on)
            raw = await _generate_one_batch(batch_spec)
            valid, batch_deficit = validate_batch_aligned(
                raw, batch_spec, expected_section=batch_spec["section_name"]
            )

            valid, verify_deficit = await _apply_verification(valid, batch_spec)
            batch_deficit.extend(verify_deficit)

            for q in valid:
                q["_paper"] = exam.paper if batch_spec["is_ga"] is False else "GA"

            all_questions.extend(valid)
            completed += len(valid)
            deficit_slots.extend(batch_deficit)

            logger.info(
                f"Batch {batch_idx + 1}/{len(batches)}: "
                f"{len(valid)}/{batch_spec['count']} valid"
            )

        except Exception as exc:
            logger.error(f"Batch {batch_idx + 1} failed entirely: {exc}")
            for slot_type in question_slots_from_batch(batch_spec):
                deficit_slots.append(slot_spec_from_batch(batch_spec, slot_type))

        await _update_generation_progress(
            db,
            exam,
            completed=completed,
            deficit=len(deficit_slots),
            batch=f"{batch_idx + 1}/{len(batches)}",
            phase="generating",
        )

    logger.info(
        f"Primary pass done: {len(all_questions)} valid, "
        f"{len(deficit_slots)} deficit slot(s)"
    )

    # ── 4b. Retry deficit slots (same section / type / marks / topics) ──
    if deficit_slots and len(all_questions) < GATE_TOTAL_QUESTIONS:
        retried = await _retry_deficit_slots(
            db=db,
            exam=exam,
            all_questions=all_questions,
            deficit_slots=deficit_slots,
            target=GATE_TOTAL_QUESTIONS,
        )
        completed = len(all_questions)
        deficit_slots = retried

    failed = len(deficit_slots)
    logger.info(
        f"Generation done: {len(all_questions)} valid questions "
        f"({completed} completed, {failed} still missing after retries)"
    )

    if len(all_questions) < 20:
        raise ValueError(
            f"Only generated {len(all_questions)} valid questions — "
            "not enough to assemble an exam. Check LLM configuration."
        )

    # ── 5. Store questions in question_bank ──
    stored_ids = await _store_questions(db, all_questions, exam)

    # Tag each question dict with its stored UUID BEFORE assembly.
    # stored_ids[i] corresponds to all_questions[i] by position (see
    # _store_questions). assemble_exam reads this "_stored_id" off each
    # selected dict, so every question_order entry comes out with the correct
    # question_id — no positional post-fix required.
    for i, q in enumerate(all_questions):
        q["_stored_id"] = str(stored_ids[i])

    # ── 6. Assemble exam ──
    question_order, _selected = assemble_exam(all_questions, exam.paper)

    summary = compute_marks_summary(question_order)
    logger.info(f"Exam assembled: {summary}")

    # ── 7. Update exam row ──
    # question_ids = ordered list of UUID strings matching question_order
    exam.question_ids = [entry["question_id"] for entry in question_order]
    exam.question_order = question_order
    # Reconcile the headline totals with what was actually assembled. If
    # generation fell short of the standard 65 questions / 100 marks, scoring
    # and percentages must use the real totals, not the optimistic defaults.
    exam.total_questions = summary["total_questions"]
    exam.total_marks = summary["total_marks"]
    exam.status = "generated"
    exam.generation_progress = {
        "total": GATE_TOTAL_QUESTIONS,
        "completed": len(question_order),
        "failed": failed,
        "phase": "complete",
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
        "question_slots": ["MCQ"] * GA_1MARK,
        # GATE GA is not trivial: floor the 1-mark auto difficulty at medium (was easy).
        "difficulty": difficulty if difficulty != "auto" else "medium",
    })
    batches.append({
        "section_name": "General Aptitude",
        "paper": paper,
        "is_ga": True,
        "topics": all_ga_topics,
        "marks": 2,
        "count": GA_2MARK,
        "types": {"MCQ": GA_2MARK},
        "question_slots": ["MCQ"] * GA_2MARK,
        # 2-mark GA needs genuine multi-step reasoning: floor auto difficulty at hard (was medium).
        "difficulty": difficulty if difficulty != "auto" else "hard",
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
                    "question_slots": list(chunk),
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

    slots = question_slots_from_batch(batch_spec)
    specs_lines = [
        f"{idx}. {qtype}, {batch_spec['marks']} mark(s)"
        for idx, qtype in enumerate(slots, start=1)
    ]
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

    # Prepend retrieved previous-year exemplars (if grounding attached any).
    exemplars = batch_spec.get("exemplars")
    if exemplars:
        user_prompt = format_exemplars(exemplars) + "\n\n" + user_prompt

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


async def _apply_verification(
    valid: list[dict],
    batch_spec: dict,
) -> tuple[list[dict], list[dict]]:
    """Optional LLM verification gate over structurally-valid questions.

    Disabled by default (settings.LLM_VERIFY_ENABLED). When enabled, rejected
    questions are returned as deficit slots so the retry loop regenerates them.
    The off-path is a pure no-op: no LLM calls and no behaviour change.
    """
    if not settings.LLM_VERIFY_ENABLED or not valid:
        return valid, []

    kept, rejected = await verify_questions(valid, batch_spec["difficulty"])
    extra_deficit = [
        slot_spec_from_batch(batch_spec, q.get("question_type"))
        for q in rejected
    ]
    if rejected:
        logger.info(
            "Verification gate rejected %s/%s question(s) in this batch",
            len(rejected),
            len(valid),
        )
    return kept, extra_deficit


async def _attach_exemplars(
    db: AsyncSession,
    batch_spec: dict,
    *,
    enabled: bool,
) -> None:
    """Retrieve PYQ exemplars for a batch and attach them to the spec.

    No-op (and never raises) when grounding is disabled or retrieval is empty,
    so generation falls back to its previous ungrounded behaviour.
    """
    if not enabled:
        return
    try:
        rows = await retrieve_exemplars(
            db,
            paper=batch_spec["paper"],
            section_name=batch_spec["section_name"],
            topics=batch_spec.get("topics", []),
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not attach PYQ exemplars (continuing): %s", exc)
        return
    if rows:
        batch_spec["exemplars"] = rows
        logger.info(
            "Attached %s PYQ exemplar(s) to batch (%s / %s)",
            len(rows),
            batch_spec["paper"],
            batch_spec["section_name"],
        )


async def _update_generation_progress(
    db: AsyncSession,
    exam: Exam,
    *,
    completed: int,
    deficit: int,
    batch: str,
    phase: str,
    retry_round: int | None = None,
) -> None:
    progress: dict = {
        "total": GATE_TOTAL_QUESTIONS,
        "completed": min(completed, GATE_TOTAL_QUESTIONS),
        "failed": deficit,
        "batch": batch,
        "phase": phase,
    }
    if retry_round is not None:
        progress["retry_round"] = retry_round
    exam.generation_progress = progress
    await db.commit()


def _slot_group_key(slot: dict) -> tuple:
    return (
        slot["section_name"],
        slot["marks"],
        slot["difficulty"],
        slot["is_ga"],
        tuple(slot["topics"]),
    )


def _group_deficit_for_retry(
    slots: list[dict],
    max_size: int,
) -> list[list[dict]]:
    """Group deficit slots into small retry batches with matching syllabus context."""
    if not slots:
        return []

    groups: list[list[dict]] = []
    current: list[dict] = []
    current_key = None

    for slot in slots:
        key = _slot_group_key(slot)
        if current and (key != current_key or len(current) >= max_size):
            groups.append(current)
            current = []
        current.append(slot)
        current_key = key

    if current:
        groups.append(current)
    return groups


def _batch_spec_from_deficit_group(group: list[dict]) -> dict:
    """Build a generation batch spec from one or more deficit slots."""
    first = group[0]
    slots = [s["question_type"] for s in group]
    type_counts: dict[str, int] = {}
    for qtype in slots:
        type_counts[qtype] = type_counts.get(qtype, 0) + 1

    return {
        "section_name": first["section_name"],
        "paper": first["paper"],
        "is_ga": first["is_ga"],
        "topics": list(first["topics"]),
        "marks": first["marks"],
        "count": len(slots),
        "types": type_counts,
        "question_slots": slots,
        "difficulty": first["difficulty"],
    }


async def _retry_deficit_slots(
    db: AsyncSession,
    exam: Exam,
    all_questions: list[dict],
    deficit_slots: list[dict],
    target: int,
) -> list[dict]:
    """
    Retry generation for deficit slots after the primary pass.

    Returns the list of slots that could not be filled after all retry rounds.
    Mutates *all_questions* in place when retries succeed.
    """
    remaining = list(deficit_slots)
    grounding_on = settings.PYQ_GROUNDING_ENABLED and bool(exam.use_pyq_reference)
    max_rounds = settings.GENERATION_DEFICIT_MAX_ROUNDS
    batch_size = max(1, settings.GENERATION_DEFICIT_BATCH_SIZE)
    round_delay = max(0, settings.GENERATION_DEFICIT_ROUND_DELAY_SECONDS)

    logger.info(
        "Starting deficit retry: %s slot(s) to fill (have %s/%s)",
        len(remaining),
        len(all_questions),
        target,
    )

    for retry_round in range(1, max_rounds + 1):
        if not remaining or len(all_questions) >= target:
            break

        if retry_round > 1 and round_delay > 0:
            wait = round_delay * retry_round
            logger.info("Deficit retry round %s: waiting %ss before retry", retry_round, wait)
            await asyncio.sleep(wait)

        next_remaining: list[dict] = []
        groups = _group_deficit_for_retry(remaining, batch_size)
        logger.info(
            "Deficit retry round %s/%s: %s slot(s) in %s group(s)",
            retry_round,
            max_rounds,
            len(remaining),
            len(groups),
        )

        for group_idx, group in enumerate(groups):
            retry_spec = _batch_spec_from_deficit_group(group)
            batch_label = f"retry {retry_round}/{max_rounds} · group {group_idx + 1}/{len(groups)}"

            try:
                await _attach_exemplars(db, retry_spec, enabled=grounding_on)
                raw = await _generate_one_batch(retry_spec)
                valid, still_failed = validate_batch_aligned(
                    raw,
                    retry_spec,
                    expected_section=retry_spec["section_name"],
                )

                valid, verify_deficit = await _apply_verification(valid, retry_spec)
                still_failed.extend(verify_deficit)

                for q in valid:
                    q["_paper"] = (
                        exam.paper if retry_spec["is_ga"] is False else "GA"
                    )

                all_questions.extend(valid)
                next_remaining.extend(still_failed)

                logger.info(
                    "Deficit %s: %s/%s slot(s) filled",
                    batch_label,
                    len(valid),
                    len(group),
                )

            except Exception as exc:
                logger.error("Deficit %s failed: %s", batch_label, exc)
                next_remaining.extend(group)
                if round_delay > 0:
                    await asyncio.sleep(round_delay)

            slots_still_pending = len(next_remaining) + sum(
                len(g) for g in groups[group_idx + 1 :]
            )
            await _update_generation_progress(
                db,
                exam,
                completed=len(all_questions),
                deficit=slots_still_pending,
                batch=batch_label,
                phase="retry",
                retry_round=retry_round,
            )

        remaining = next_remaining
        logger.info(
            "Deficit retry round %s complete: %s slot(s) still missing",
            retry_round,
            len(remaining),
        )

    if remaining:
        logger.warning(
            "%s question slot(s) could not be generated after %s retry round(s)",
            len(remaining),
            max_rounds,
        )

    return remaining


async def _store_questions(
    db: AsyncSession,
    questions: list[dict],
    exam: Exam,
) -> list[uuid.UUID]:
    """Store generated questions in the question_bank table."""
    stored_ids: list[uuid.UUID] = []
    llm_metadata = get_active_llm_metadata()

    for q in questions:
        q = sanitize_question_fields(q)
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
            llm_provider=llm_metadata["provider"],
            llm_model=llm_metadata["model"],
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
