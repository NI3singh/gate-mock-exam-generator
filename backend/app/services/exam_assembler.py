"""
Exam assembler: selects exactly 65 questions following GATE 2026 distribution,
stores them in question_bank, and updates the exam record.
"""

import uuid
from typing import Any

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exam import Exam
from app.models.question_bank import QuestionBank


# ─── GATE 2026 distribution constants ───────────────────────────────────────

GA_1MARK_COUNT = 5
GA_2MARK_COUNT = 5
SUBJECT_1MARK_COUNT = 25
SUBJECT_2MARK_COUNT = 30


# ─── Difficulty score mapping ────────────────────────────────────────────────


def _difficulty_to_score(difficulty: str) -> float:
    mapping = {"easy": 0.3, "medium": 0.6, "hard": 0.9}
    return mapping.get(difficulty, 0.5)


# ─── Progress updater ─────────────────────────────────────────────────────────


async def update_exam_progress(
    db: AsyncSession,
    exam_id: str,
    completed: int,
    failed: int,
) -> None:
    """Update the generation_progress JSON on the exam row."""
    total = completed + failed
    await db.execute(
        update(Exam)
        .where(Exam.id == exam_id)
        .values(
            generation_progress={
                "total": 65,
                "completed": completed,
                "failed": failed,
            }
        )
    )
    await db.commit()


# ─── Question selection ───────────────────────────────────────────────────────


def select_65_questions(
    all_questions: list[dict[str, Any]],
    types_ratio: dict[str, float],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    From all generated questions, select exactly 65 following GATE distribution.

    Returns (ga_questions, subject_questions).

    GA: 5×1mark + 5×2mark = 10 questions
    Subject: 25×1mark + 30×2mark = 55 questions
    """
    ga_qs = [q for q in all_questions if q.get("paper") == "GA"]
    subject_qs = [q for q in all_questions if q.get("paper") != "GA"]

    # Trim/pad GA to exactly 10
    ga_1mark = [q for q in ga_qs if q.get("marks") == 1][:GA_1MARK_COUNT]
    ga_2mark = [q for q in ga_qs if q.get("marks") == 2][:GA_2MARK_COUNT]
    ga_qs = ga_1mark + ga_2mark

    # Trim subject to at most 60 (we'll select exactly 55)
    subject_1mark = [q for q in subject_qs if q.get("marks") == 1]
    subject_2mark = [q for q in subject_qs if q.get("marks") == 2]

    # Apply type ratio within 2-mark subject questions
    mcq_1mark = [q for q in subject_1mark if q.get("question_type") == "MCQ"]
    mcq_2mark = [q for q in subject_2mark if q.get("question_type") == "MCQ"]
    msq_2mark = [q for q in subject_2mark if q.get("question_type") == "MSQ"]
    nat_2mark = [q for q in subject_2mark if q.get("question_type") == "NAT"]

    target_mcq_1mark = int(SUBJECT_1MARK_COUNT * types_ratio.get("MCQ", 0.6))
    target_mcq_2mark = int(SUBJECT_2MARK_COUNT * types_ratio.get("MCQ", 0.6))
    target_msq = int(SUBJECT_2MARK_COUNT * types_ratio.get("MSQ", 0.2))
    target_nat = int(SUBJECT_2MARK_COUNT * types_ratio.get("NAT", 0.2))

    selected_subject = (
        mcq_1mark[:target_mcq_1mark]
        + mcq_2mark[:target_mcq_2mark]
        + msq_2mark[:target_msq]
        + nat_2mark[:target_nat]
    )

    # Ensure we have exactly 55 subject questions — pad with whatever is available
    while len(selected_subject) < 55:
        for pool in [mcq_2mark, msq_2mark, nat_2mark]:
            for q in pool:
                if q not in selected_subject and len(selected_subject) < 55:
                    selected_subject.append(q)

    return ga_qs, selected_subject[:55]


# ─── Question ordering ────────────────────────────────────────────────────────


def build_question_order(
    ga_qs: list[dict[str, Any]],
    subject_qs: list[dict[str, Any]],
) -> list[str]:
    """
    Build final question ordering:
      - GA questions first (Q1–Q10)
      - Subject questions next (Q11–Q65)
      - Within each group, interleave by marks: 1mark, 1mark, 2mark, 2mark, ...

    Returns list of question IDs (UUID strings).
    """

    def interleaved(qs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        one = [q for q in qs if q.get("marks") == 1]
        two = [q for q in qs if q.get("marks") == 2]
        result: list[dict[str, Any]] = []
        for o, t in zip(one, two):
            result.extend([o, t])
        if len(one) > len(two):
            result.extend(one[len(two) :])
        elif len(two) > len(one):
            result.extend(two[len(one) :])
        return result

    ordered = interleaved(ga_qs) + interleaved(subject_qs)
    return [q.get("id") or str(uuid.uuid4()) for q in ordered]


# ─── Question insertion ───────────────────────────────────────────────────────


async def insert_questions(
    db: AsyncSession,
    questions: list[dict[str, Any]],
    exam_id: str,
) -> list[str]:
    """
    Insert validated question dicts into the question_bank table.
    Returns list of inserted question ID strings.
    """
    inserted_ids: list[str] = []

    for q in questions:
        q_id = uuid.uuid4()
        row = QuestionBank(
            id=q_id,
            paper=q.get("paper", "CS"),
            question_type=q["question_type"],
            marks=q["marks"],
            difficulty=q["difficulty"],
            difficulty_score=_difficulty_to_score(q["difficulty"]),
            section_name=q["section_name"],
            topic=q["topic"],
            stem_tex=q["stem_tex"],
            code_snippet=q.get("code_snippet"),
            code_language=q.get("code_language"),
            choices=q.get("choices"),
            answer=q["answer"],
            solution_tex=q["solution_tex"],
            estimated_time_seconds=q.get("estimated_time_seconds", 180),
            provenance=[{"exam_id": exam_id}],
            llm_model="deepseek-ai/DeepSeek-V3.2",
            llm_prompt_version="1.0",
            validated=True,
            validation_notes="Auto-validated by question_validator",
        )
        db.add(row)
        inserted_ids.append(str(q_id))

    await db.flush()
    return inserted_ids


# ─── Final assembly ───────────────────────────────────────────────────────────


async def assemble_exam(
    db: AsyncSession,
    exam_id: str,
    all_questions: list[dict[str, Any]],
    types_ratio: dict[str, float],
) -> None:
    """
    Final assembly step:
      1. Select exactly 65 questions following GATE distribution
      2. Build ordering (GA first, then Subject)
      3. Insert into question_bank
      4. Update exam with question_ids, question_order, status="generated"
    """
    ga_qs, subject_qs = select_65_questions(all_questions, types_ratio)
    ordered_ids = build_question_order(ga_qs, subject_qs)
    all_selected = ga_qs + subject_qs

    inserted_ids = await insert_questions(db, all_selected, exam_id)

    await db.execute(
        update(Exam)
        .where(Exam.id == exam_id)
        .values(
            question_ids=inserted_ids,
            question_order=ordered_ids,
            status="generated",
            generation_progress={
                "total": 65,
                "completed": len(inserted_ids),
                "failed": 0,
            },
        )
    )
    await db.commit()
