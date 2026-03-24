from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attempt import Attempt
from app.models.exam import Exam
from app.models.question_bank import QuestionBank


# ── Marking functions ──────────────────────────────────────────────────────────

def grade_mcq(
    user_answer: dict | None, correct: dict, marks: int
) -> tuple[float, bool, bool]:
    """
    Grade an MCQ question.
    Returns (score, is_correct, is_wrong).
    Correct: +marks. Wrong: −marks/3. Unanswered: 0.
    """
    if user_answer is None:
        return 0.0, False, False
    if user_answer.get("index") == correct.get("index"):
        return float(marks), True, False
    neg = round(marks / 3, 6)
    return -neg, False, True


def grade_msq(
    user_answer: dict | None, correct: dict, marks: int
) -> tuple[float, bool, bool]:
    """
    Grade an MSQ question (all-or-nothing).
    Returns (score, is_correct, is_wrong).
    Correct: +marks. Wrong/Unanswered: 0. No negative marking.
    """
    if user_answer is None:
        return 0.0, False, False
    indices = user_answer.get("indices", [])
    if not indices:
        return 0.0, False, False
    user_set = set(indices)
    correct_set = set(correct.get("indices", []))
    if user_set == correct_set:
        return float(marks), True, False
    return 0.0, False, True


def grade_nat(
    user_answer: dict | None, correct: dict, marks: int
) -> tuple[float, bool, bool]:
    """
    Grade a NAT question (range-based tolerance).
    Returns (score, is_correct, is_wrong).
    Correct: +marks (within tolerance). Wrong/Unanswered: 0. No negative marking.
    """
    if user_answer is None:
        return 0.0, False, False
    value_str = user_answer.get("value", "").strip()
    if not value_str:
        return 0.0, False, False
    try:
        user_val = float(value_str)
    except (ValueError, TypeError):
        return 0.0, False, True
    tolerance = correct.get("tolerance", 0.01)
    if abs(user_val - correct.get("value", 0)) <= tolerance:
        return float(marks), True, False
    return 0.0, False, True


# ── Main grading function ──────────────────────────────────────────────────────

async def grade_attempt(db: AsyncSession, attempt_id: str) -> dict[str, Any]:
    """
    Grade a complete exam attempt and update the Attempt row.
    Returns a dict with the full result breakdown.
    """
    # 1. Fetch attempt
    result = await db.execute(select(Attempt).where(Attempt.id == attempt_id))
    attempt: Attempt | None = result.scalar_one_or_none()
    if attempt is None:
        raise ValueError(f"Attempt {attempt_id} not found")

    # 2. Fetch exam
    exam_result = await db.execute(select(Exam).where(Exam.id == attempt.exam_id))
    exam: Exam | None = exam_result.scalar_one_or_none()
    if exam is None:
        raise ValueError(f"Exam {attempt.exam_id} not found")

    question_order: list[str] = exam.question_order or []
    responses: dict[str, Any] = attempt.responses or {}

    # 3. Fetch all question bank rows for this exam (in one query)
    question_ids = question_order
    q_result = await db.execute(
        select(QuestionBank).where(QuestionBank.id.in_(question_ids))
    )
    questions: list[QuestionBank] = q_result.scalars().all()
    question_map: dict[str, QuestionBank] = {str(q.id): q for q in questions}

    # 4. Grade each question
    total_score = 0.0
    total_correct = 0
    total_wrong = 0
    total_unanswered = 0

    # Breakdown by section (GA / Subject)
    section_scores: dict[str, dict[str, Any]] = {
        "GA":    {"correct": 0, "wrong": 0, "unanswered": 0, "score": 0.0, "max_score": 0},
        "Subject": {"correct": 0, "wrong": 0, "unanswered": 0, "score": 0.0, "max_score": 0},
    }

    # Breakdown by question type
    type_scores: dict[str, dict[str, Any]] = {
        "MCQ": {"correct": 0, "wrong": 0, "unanswered": 0, "score": 0.0},
        "MSQ": {"correct": 0, "wrong": 0, "unanswered": 0, "score": 0.0},
        "NAT": {"correct": 0, "wrong": 0, "unanswered": 0, "score": 0.0},
    }

    # Topic analysis
    topic_data: dict[str, dict[str, Any]] = {}

    for q_id in question_order:
        q: QuestionBank | None = question_map.get(q_id)
        if q is None:
            continue

        user_answer = responses.get(q_id)
        correct = q.answer
        marks = q.marks
        qtype = q.question_type
        section = q.section_name  # "GA" or a subject section name
        topic = q.topic

        # Determine section bucket
        section_bucket = "GA" if section.upper() == "GA" else "Subject"

        # Grade per type
        if qtype == "MCQ":
            score, is_correct, is_wrong = grade_mcq(user_answer, correct, marks)
        elif qtype == "MSQ":
            score, is_correct, is_wrong = grade_msq(user_answer, correct, marks)
        elif qtype == "NAT":
            score, is_correct, is_wrong = grade_nat(user_answer, correct, marks)
        else:
            score, is_correct, is_wrong = 0.0, False, False

        total_score += score
        section_scores[section_bucket]["max_score"] += marks

        if is_correct:
            total_correct += 1
            section_scores[section_bucket]["correct"] += 1
            type_scores[qtype]["correct"] += 1
        elif is_wrong:
            total_wrong += 1
            section_scores[section_bucket]["wrong"] += 1
            type_scores[qtype]["wrong"] += 1
        else:
            total_unanswered += 1
            section_scores[section_bucket]["unanswered"] += 1
            type_scores[qtype]["unanswered"] += 1

        section_scores[section_bucket]["score"] += score
        type_scores[qtype]["score"] += score

        # Topic tracking
        topic_key = topic
        if topic_key not in topic_data:
            topic_data[topic_key] = {
                "topic": topic_key,
                "section_name": section,
                "total": 0,
                "correct": 0,
                "wrong": 0,
                "unanswered": 0,
                "score": 0.0,
                "max_score": 0,
            }
        topic_data[topic_key]["total"] += 1
        topic_data[topic_key]["max_score"] += marks
        if is_correct:
            topic_data[topic_key]["correct"] += 1
        elif is_wrong:
            topic_data[topic_key]["wrong"] += 1
        else:
            topic_data[topic_key]["unanswered"] += 1
        topic_data[topic_key]["score"] += score

    topic_analysis = list(topic_data.values())

    # 5. Build score_breakdown
    score_breakdown = {
        "section": section_scores,
        "type": type_scores,
    }

    # 6. Update attempt
    now = datetime.now(timezone.utc)
    attempt.score = round(total_score, 6)
    attempt.total_correct = total_correct
    attempt.total_wrong = total_wrong
    attempt.total_unanswered = total_unanswered
    attempt.score_breakdown = score_breakdown
    attempt.topic_analysis = topic_analysis
    attempt.submitted = True
    attempt.end_time = now

    # 7. Update exam status
    await db.execute(
        update(Exam)
        .where(Exam.id == attempt.exam_id)
        .values(status="completed")
    )

    await db.commit()

    return {
        "attempt_id": str(attempt.id),
        "exam_id": str(exam.id),
        "paper": exam.paper,
        "difficulty": exam.difficulty,
        "total_questions": exam.total_questions,
        "total_marks": exam.total_marks,
        "duration_minutes": exam.duration_minutes,
        "score": attempt.score,
        "max_score": attempt.max_score,
        "total_correct": total_correct,
        "total_wrong": total_wrong,
        "total_unanswered": total_unanswered,
        "score_breakdown": score_breakdown,
        "section_scores": section_scores,
        "topic_analysis": topic_analysis,
        "violations_count": len(attempt.events_log or []),
    }
