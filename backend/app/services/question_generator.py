"""
Question generator orchestrator.

Drives the full generation pipeline:
  1. Retrieve syllabus context from DB
  2. Generate GA questions (2 batches × 5 = 10)
  3. Generate subject questions (11 batches × 5 = 55)
  4. Validate each question with retry logic
  5. Update progress after every batch
"""

import json
import random
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.syllabus import Syllabus
from app.services.llm_service import llm_service
from app.services.question_validator import validate_question_with_retry
from app.services.exam_assembler import update_exam_progress

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


# ─── Template loader ─────────────────────────────────────────────────────────


def load_template(name: str) -> dict[str, Any]:
    """Load a JSON prompt template from the prompts directory."""
    with open(PROMPTS_DIR / f"{name}.json", encoding="utf-8") as f:
        return json.load(f)


# ─── Syllabus context builder ───────────────────────────────────────────────


def build_syllabus_context(
    paper: str,
    topics: list[str] | None,
    db: AsyncSession,
) -> str:
    """
    Query the syllabus table for the given paper (and optional topic filter),
    group by section_name, and return a formatted string for the LLM prompt.
    """
    query = select(Syllabus).where(Syllabus.paper == paper)
    if topics:
        query = query.where(Syllabus.topic.in_(topics))
    result = db.execute(query)
    rows = result.scalars().all()

    sections: dict[str, list[str]] = {}
    for row in rows:
        sections.setdefault(row.section_name, []).append(row.topic)

    lines: list[str] = []
    for section, topic_list in sections.items():
        lines.append(f"## {section}")
        for t in topic_list:
            lines.append(f"  - {t}")
        lines.append("")

    return "\n".join(lines) if lines else "No specific topics defined."


# ─── Batch type determination ────────────────────────────────────────────────


def determine_batch_types(
    types_ratio: dict[str, float],
    batch_size: int = 5,
) -> list[dict[str, Any]]:
    """
    For a batch of 5 questions, determine types and marks following GATE style.
    Pattern: 2×MCQ-1mark + 2×MCQ-2mark + 1×(MSQ or NAT)-2mark
    The MSQ/NAT choice is weighted randomly by the configured ratios.
    """
    batch = [
        {"question_type": "MCQ", "marks": 1},
        {"question_type": "MCQ", "marks": 1},
        {"question_type": "MCQ", "marks": 2},
        {"question_type": "MCQ", "marks": 2},
    ]

    msq_ratio = types_ratio.get("MSQ", 0.2)
    nat_ratio = types_ratio.get("NAT", 0.2)
    total = msq_ratio + nat_ratio + 0.0001  # avoid div-by-zero

    r = random.random()
    if r < msq_ratio / total:
        batch.append({"question_type": "MSQ", "marks": 2})
    else:
        batch.append({"question_type": "NAT", "marks": 2})

    return batch


# ─── GA batch generation ─────────────────────────────────────────────────────


async def generate_ga_batch(
    db: AsyncSession,
    difficulty: str,
    batch_index: int,
) -> list[dict[str, Any]]:
    """
    Generate one batch of 5 General Aptitude questions.
    - Batch 0: all 1-mark MCQ
    - Batch 1: 4×MCQ-2mark + 1×(MSQ or NAT)-2mark
    """
    template = load_template("generate_ga")
    syllabus_context = build_syllabus_context("GA", None, db)

    if batch_index == 0:
        marks_dist = "MCQ-1mark, MCQ-1mark, MCQ-1mark, MCQ-1mark, MCQ-1mark"
        types_str = "MCQ, MCQ, MCQ, MCQ, MCQ"
    else:
        # Batch 1: 2mark questions with MSQ/NAT mix
        marks_dist = "MCQ-2mark, MCQ-2mark, MCQ-2mark, MCQ-2mark, MSQ-2mark"
        types_str = "MCQ, MCQ, MCQ, MCQ, MSQ"

    user_content = json.dumps({
        "syllabus_context": syllabus_context,
        "difficulty": difficulty,
        "question_types": types_str,
        "marks_distribution": marks_dist,
    })

    messages = [
        {"role": "system", "content": template["system_prompt"]},
        {"role": "user", "content": user_content},
    ]

    try:
        raw = await llm_service.chat_completion(messages)
        questions: list[dict[str, Any]] = raw if isinstance(raw, list) else []
    except Exception as exc:
        print(f"[question_generator] GA batch {batch_index} LLM call failed: {exc}")
        questions = []

    # Add paper tag to each question
    validated: list[dict[str, Any]] = []
    for q in questions:
        q["paper"] = "GA"
        result = await validate_question_with_retry(q)
        if result.valid:
            validated.append(q)

    return validated


# ─── Subject batch generation ────────────────────────────────────────────────


async def generate_subject_batch(
    db: AsyncSession,
    paper: str,
    difficulty: str,
    types_ratio: dict[str, float],
    batch_index: int,
    topics: list[str] | None,
) -> list[dict[str, Any]]:
    """
    Generate one batch of 5 subject questions for CS or DA paper.
    """
    template = load_template("generate_batch")
    syllabus_context = build_syllabus_context(paper, topics, db)
    type_spec = determine_batch_types(types_ratio)

    marks_dist = ", ".join(
        f"{t['question_type']}-{t['marks']}mark" for t in type_spec
    )
    types_str = ", ".join(t["question_type"] for t in type_spec)

    user_content = json.dumps({
        "paper": paper,
        "difficulty": difficulty,
        "syllabus_context": syllabus_context,
        "question_types": types_str,
        "marks_distribution": marks_dist,
    })

    messages = [
        {"role": "system", "content": template["system_prompt"]},
        {"role": "user", "content": user_content},
    ]

    try:
        raw = await llm_service.chat_completion(messages)
        questions: list[dict[str, Any]] = raw if isinstance(raw, list) else []
    except Exception as exc:
        print(f"[question_generator] Subject batch {batch_index} LLM call failed: {exc}")
        questions = []

    validated: list[dict[str, Any]] = []
    for q in questions:
        q["paper"] = paper
        result = await validate_question_with_retry(q)
        if result.valid:
            validated.append(q)

    return validated


# ─── Full exam generation orchestrator ──────────────────────────────────────


async def generate_exam_questions(
    db: AsyncSession,
    exam_id: str,
    paper: str,
    scope: str,
    selected_topics: list[str] | None,
    difficulty: str,
    types_ratio: dict[str, float],
) -> tuple[list[dict[str, Any]], int]:
    """
    Orchestrates full exam generation for one exam.

    Returns (all_validated_questions, failed_count).

    Generation order:
      - 2 GA batches × 5 = 10 questions
      - 11 subject batches × 5 = 55 questions
      Total: 65 questions
    """
    all_questions: list[dict[str, Any]] = []
    failed_count = 0

    topics_filter = selected_topics if scope == "topic" else None

    # ── GA questions (2 batches) ──
    for batch_i in range(2):
        batch = await generate_ga_batch(db, difficulty, batch_i)
        all_questions.extend(batch)
        failed_in_batch = 5 - len(batch)
        failed_count += failed_in_batch
        await update_exam_progress(
            db, exam_id, completed=len(all_questions), failed=failed_count
        )

    # ── Subject questions (11 batches) ──
    for batch_i in range(11):
        batch = await generate_subject_batch(
            db, paper, difficulty, types_ratio, batch_i, topics_filter
        )
        all_questions.extend(batch)
        failed_in_batch = 5 - len(batch)
        failed_count += failed_in_batch
        await update_exam_progress(
            db, exam_id, completed=len(all_questions), failed=failed_count
        )

    return all_questions, failed_count
