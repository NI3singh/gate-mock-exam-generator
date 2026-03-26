from datetime import datetime, timezone
from typing import Any
import io

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.attempt import Attempt
from app.models.exam import Exam
from app.models.question_bank import QuestionBank
from app.schemas.attempt import (
    AttemptSaveRequest,
    AttemptSaveResponse,
    AttemptEventRequest,
    AttemptEventResponse,
    AttemptSubmitResponse,
    SolutionItem,
    ViolationSummary,
    AttemptDetailResponse,
)
from app.services.grading_engine import grade_attempt

router = APIRouter()


# ── PUT /attempts/{attempt_id}/save ─────────────────────────────────────────────


@router.put(
    "/{attempt_id}/save",
    response_model=AttemptSaveResponse,
    summary="Auto-save attempt responses and statuses",
)
async def save_attempt(
    attempt_id: str,
    body: AttemptSaveRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Saves the current responses and question statuses for an in-progress attempt.
    Called automatically by the frontend every 5 seconds (debounced).
    """
    result = await db.execute(
        select(Attempt).where(
            Attempt.id == attempt_id,
            Attempt.user_id == user.id,
        )
    )
    attempt = result.scalar_one_or_none()

    if attempt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found.",
        )

    if attempt.submitted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attempt has already been submitted.",
        )

    # Update responses and question statuses
    attempt.responses = body.responses
    attempt.question_statuses = body.question_statuses
    await db.commit()

    now = datetime.now(timezone.utc)
    return AttemptSaveResponse(
        saved=True,
        timestamp=now.isoformat(),
    )


# ── POST /attempts/{attempt_id}/event ─────────────────────────────────────────


@router.post(
    "/{attempt_id}/event",
    response_model=AttemptEventResponse,
    summary="Log an anti-cheat event",
)
async def log_attempt_event(
    attempt_id: str,
    body: AttemptEventRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Logs an anti-cheat event (e.g., fullscreen exit, visibility hidden,
    right-click, copy/paste attempt, window blur, beforeunload).
    """
    result = await db.execute(
        select(Attempt).where(
            Attempt.id == attempt_id,
            Attempt.user_id == user.id,
        )
    )
    attempt = result.scalar_one_or_none()

    if attempt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found.",
        )

    if attempt.submitted:
        # Silently ignore events for submitted attempts
        return AttemptEventResponse(logged=False)

    # Append event to events_log
    event_entry = {
        "event_type": body.event_type,
        "detail": body.detail,
        "timestamp": body.timestamp,
    }

    events_log = list(attempt.events_log or [])
    events_log.append(event_entry)
    attempt.events_log = events_log
    await db.commit()

    return AttemptEventResponse(logged=True)


# ── POST /attempts/{attempt_id}/submit ─────────────────────────────────────────


@router.post(
    "/{attempt_id}/submit",
    response_model=AttemptSubmitResponse,
    summary="Submit exam attempt and trigger grading",
)
async def submit_attempt(
    attempt_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submits an exam attempt, triggers grading, and returns the result.
    """
    result = await db.execute(
        select(Attempt).where(
            Attempt.id == attempt_id,
            Attempt.user_id == user.id,
        )
    )
    attempt = result.scalar_one_or_none()

    if attempt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found.",
        )

    if attempt.submitted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attempt has already been submitted.",
        )

    try:
        result_data = await grade_attempt(db, attempt_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Grading failed: {exc}",
        )

    return AttemptSubmitResponse(**result_data)


# ── GET /attempts/{attempt_id} ─────────────────────────────────────────────────


@router.get(
    "/{attempt_id}",
    response_model=AttemptDetailResponse,
    summary="Get graded attempt details with solutions",
)
async def get_attempt_detail(
    attempt_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns the full graded result including per-question solutions
    and anti-cheat violation summary.
    """
    result = await db.execute(
        select(Attempt).where(
            Attempt.id == attempt_id,
            Attempt.user_id == user.id,
        )
    )
    attempt: Attempt | None = result.scalar_one_or_none()

    if attempt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found.",
        )

    # Fetch exam
    exam_result = await db.execute(select(Exam).where(Exam.id == attempt.exam_id))
    exam: Exam | None = exam_result.scalar_one_or_none()
    if exam is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found.",
        )

    # FIX: question_order is stored as list[dict] e.g.
    # [{"qno": 1, "question_id": "uuid-str", "marks": 1, ...}, ...]
    # Extract the string UUID from each entry before querying the DB.
    question_order_raw: list = exam.question_order or []
    question_order: list[str] = [
        entry["question_id"]
        for entry in question_order_raw
        if isinstance(entry, dict) and entry.get("question_id")
    ]

    # Fetch all question bank rows for this exam
    q_result = await db.execute(
        select(QuestionBank).where(QuestionBank.id.in_(question_order))
    )
    questions: list[QuestionBank] = q_result.scalars().all()
    question_map: dict[str, QuestionBank] = {str(q.id): q for q in questions}

    responses: dict[str, Any] = attempt.responses or {}

    # Build solutions list (preserve question_order ordering)
    solutions: list[SolutionItem] = []
    for idx, q_id in enumerate(question_order):
        q: QuestionBank | None = question_map.get(q_id)
        if q is None:
            continue
        user_answer = responses.get(q_id)
        correct_answer = q.answer

        # Determine is_correct and score for this question
        is_correct = False
        score_for_q = 0.0
        if q.question_type == "MCQ":
            if user_answer and user_answer.get("index") == correct_answer.get("index"):
                is_correct = True
                score_for_q = float(q.marks)
            elif user_answer:
                score_for_q = -round(q.marks / 3, 6)
        elif q.question_type == "MSQ":
            if user_answer:
                user_set = set(user_answer.get("indices", []))
                correct_set = set(correct_answer.get("indices", []))
                if user_set == correct_set:
                    is_correct = True
                    score_for_q = float(q.marks)
        elif q.question_type == "NAT":
            if user_answer and user_answer.get("value", "").strip():
                try:
                    tolerance = correct_answer.get("tolerance", 0.01)
                    if abs(float(user_answer["value"]) - correct_answer["value"]) <= tolerance:
                        is_correct = True
                        score_for_q = float(q.marks)
                except (ValueError, TypeError):
                    pass

        solutions.append(
            SolutionItem(
                qno=idx + 1,
                question_type=q.question_type,
                marks=q.marks,
                section="GA" if q.section_name.upper() == "GA" else "Subject",
                section_name=q.section_name,
                topic=q.topic,
                stem_tex=q.stem_tex,
                code_snippet=q.code_snippet,
                code_language=q.code_language,
                choices=q.choices,
                user_answer=user_answer,
                correct_answer=correct_answer,
                is_correct=is_correct,
                score=score_for_q,
                solution_tex=q.solution_tex,
            )
        )

    # Compute negative marks (MCQ wrong answers only)
    negative_marks = 0.0
    for sol in solutions:
        if sol.question_type == "MCQ" and not sol.is_correct and sol.user_answer is not None:
            negative_marks += round(sol.marks / 3, 6)
    negative_marks = round(negative_marks, 6)

    # Group violations by event type
    events_log: list[dict] = list(attempt.events_log or [])
    violation_map: dict[str, int] = {}
    for evt in events_log:
        evt_type = evt.get("event_type", "unknown")
        violation_map[evt_type] = violation_map.get(evt_type, 0) + 1
    violations = [
        ViolationSummary(event_type=k, count=v)
        for k, v in sorted(violation_map.items())
    ]

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
        score_breakdown=attempt.score_breakdown or {},
        section_scores=attempt.score_breakdown.get("section", {}) if attempt.score_breakdown else {},
        topic_analysis=attempt.topic_analysis or [],
        violations=violations,
        violations_count=len(events_log),
        solutions=solutions,
    )


# ── GET /attempts/{attempt_id}/pdf ─────────────────────────────────────────────


@router.get(
    "/{attempt_id}/pdf",
    summary="Download result as PDF",
)
async def download_result_pdf(
    attempt_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generates and streams a PDF result sheet for the given attempt.
    """
    from app.services.pdf_generator import generate_result_pdf

    try:
        pdf_bytes = await generate_result_pdf(db, attempt_id, user.id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF generation failed: {exc}",
        )

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=result_{attempt_id}.pdf"
        },
    )