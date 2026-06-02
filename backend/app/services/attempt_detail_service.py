from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attempt import Attempt
from app.models.exam import Exam
from app.models.question_bank import QuestionBank
from app.schemas.attempt import AttemptDetailResponse, SolutionItem, ViolationSummary


def _normalize_question_refs(question_order_raw: list[Any]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []

    for idx, entry in enumerate(question_order_raw or []):
        if isinstance(entry, dict) and entry.get("question_id"):
            refs.append(
                {
                    "qno": int(entry.get("qno") or idx + 1),
                    "question_id": str(entry["question_id"]),
                }
            )
            continue

        if entry:
            refs.append(
                {
                    "qno": idx + 1,
                    "question_id": str(entry),
                }
            )

    return refs


async def build_attempt_detail(
    db: AsyncSession,
    attempt_id: str,
    user_id: UUID | str,
) -> AttemptDetailResponse:
    result = await db.execute(
        select(Attempt).where(
            Attempt.id == attempt_id,
            Attempt.user_id == user_id,
        )
    )
    attempt: Attempt | None = result.scalar_one_or_none()

    if attempt is None:
        raise ValueError("Attempt not found.")

    exam_result = await db.execute(select(Exam).where(Exam.id == attempt.exam_id))
    exam: Exam | None = exam_result.scalar_one_or_none()

    if exam is None:
        raise ValueError("Exam not found.")

    question_refs = _normalize_question_refs(exam.question_order or [])
    question_ids = [ref["question_id"] for ref in question_refs]

    q_result = await db.execute(
        select(QuestionBank).where(QuestionBank.id.in_(question_ids))
    )
    questions: list[QuestionBank] = q_result.scalars().all()
    question_map: dict[str, QuestionBank] = {str(question.id): question for question in questions}

    responses: dict[str, Any] = attempt.responses or {}
    solutions: list[SolutionItem] = []

    for ref in question_refs:
        q_id = ref["question_id"]
        question = question_map.get(q_id)
        if question is None:
            continue

        user_answer = responses.get(q_id)
        correct_answer = question.answer

        is_correct = False
        score_for_q = 0.0

        if question.question_type == "MCQ":
            if user_answer and user_answer.get("index") == correct_answer.get("index"):
                is_correct = True
                score_for_q = float(question.marks)
            elif user_answer:
                score_for_q = -round(question.marks / 3, 6)
        elif question.question_type == "MSQ":
            if user_answer:
                user_set = set(user_answer.get("indices", []))
                correct_set = set(correct_answer.get("indices", []))
                if user_set == correct_set:
                    is_correct = True
                    score_for_q = float(question.marks)
        elif question.question_type == "NAT":
            if user_answer and user_answer.get("value", "").strip():
                try:
                    tolerance = correct_answer.get("tolerance", 0.01)
                    if abs(float(user_answer["value"]) - correct_answer["value"]) <= tolerance:
                        is_correct = True
                        score_for_q = float(question.marks)
                except (ValueError, TypeError):
                    pass

        solutions.append(
            SolutionItem(
                qno=ref["qno"],
                question_type=question.question_type,
                marks=question.marks,
                section=(
                    "GA"
                    if (question.section_name or "").strip().lower()
                    in ("ga", "general aptitude")
                    else "Subject"
                ),
                section_name=question.section_name,
                topic=question.topic,
                stem_tex=question.stem_tex,
                code_snippet=question.code_snippet,
                code_language=question.code_language,
                choices=question.choices,
                user_answer=user_answer,
                correct_answer=correct_answer,
                is_correct=is_correct,
                score=score_for_q,
                solution_tex=question.solution_tex,
            )
        )

    negative_marks = 0.0
    for solution in solutions:
        if (
            solution.question_type == "MCQ"
            and not solution.is_correct
            and solution.user_answer is not None
        ):
            negative_marks += round(solution.marks / 3, 6)
    negative_marks = round(negative_marks, 6)

    events_log: list[dict[str, Any]] = list(attempt.events_log or [])
    violation_map: dict[str, int] = {}
    for event in events_log:
        event_type = event.get("event_type", "unknown")
        violation_map[event_type] = violation_map.get(event_type, 0) + 1

    violations = [
        ViolationSummary(event_type=event_type, count=count)
        for event_type, count in sorted(violation_map.items())
    ]

    score_breakdown = attempt.score_breakdown or {}

    return AttemptDetailResponse(
        attempt_id=str(attempt.id),
        exam_id=str(exam.id),
        paper=exam.paper,
        difficulty=exam.difficulty,
        total_questions=exam.total_questions,
        total_marks=exam.total_marks,
        duration_minutes=exam.duration_minutes,
        score=round(attempt.score or 0.0, 6),
        max_score=attempt.max_score,
        total_correct=attempt.total_correct or 0,
        total_wrong=attempt.total_wrong or 0,
        total_unanswered=attempt.total_unanswered or 0,
        negative_marks=negative_marks,
        score_breakdown=score_breakdown,
        section_scores=score_breakdown.get("section", {}),
        topic_analysis=attempt.topic_analysis or [],
        violations=violations,
        violations_count=len(events_log),
        solutions=sorted(solutions, key=lambda item: item.qno),
    )
