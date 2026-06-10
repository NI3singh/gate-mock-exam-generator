import asyncio
import uuid as uuid_module
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from math import ceil

from fastapi import Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.exam import Exam
from app.models.attempt import Attempt
from app.models.syllabus import Syllabus
from app.models.question_bank import QuestionBank
from app.schemas.exam import (
    ExamGenerateRequest,
    ExamGenerateResponse,
    ExamSummary,
    ExamHistoryItem,
    ExamHistoryResponse,
    ExamScreenResponse,
    QuestionItem,
    AttemptStartResponse,
)
from app.services.question_generator import run_generation
from app.services.grading_engine import grade_attempt
from app.services.analytics_service import refresh_user_analytics_safely

router = APIRouter()


# ── POST /exams/generate ──────────────────────────────────────────────────────

@router.post(
    "/generate",
    response_model=ExamGenerateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create exam configuration and start generation",
)
async def generate_exam(
    body: ExamGenerateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # ── 1. Validate paper has syllabus data loaded ──
    paper_count_result = await db.execute(
        select(Syllabus.id).where(Syllabus.paper == body.paper).limit(1)
    )
    if paper_count_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No syllabus data found for paper '{body.paper}'. "
            "Please call POST /api/v1/admin/load-data first.",
        )

    # ── 2. Validate GA syllabus exists ──
    ga_count_result = await db.execute(
        select(Syllabus.id).where(Syllabus.paper == "GA").limit(1)
    )
    if ga_count_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No syllabus data found for General Aptitude (GA). "
            "Please call POST /api/v1/admin/load-data first.",
        )

    # ── 3. Validate selected_topics if scope is 'topic' ──
    if body.scope == "topic":
        if not body.selected_topics or len(body.selected_topics) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="When scope is 'topic', you must select at least one topic.",
            )
        valid_topics_result = await db.execute(
            select(Syllabus.topic).where(Syllabus.paper == body.paper)
        )
        valid_topics = {row[0] for row in valid_topics_result.fetchall()}
        invalid = [t for t in body.selected_topics if t not in valid_topics]
        if invalid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid topics for paper {body.paper}: {invalid}",
            )

    # ── 4. Validate types_ratio sums to ~1.0 ──
    ratio_sum = body.types_ratio.MCQ + body.types_ratio.MSQ + body.types_ratio.NAT
    if abs(ratio_sum - 1.0) > 0.05:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"types_ratio must sum to 1.0 (got {ratio_sum:.2f})",
        )

    # ── 5. Create exam row ──
    exam_id = uuid_module.uuid4()
    exam = Exam(
        id=exam_id,
        user_id=user.id,
        paper=body.paper,
        scope=body.scope,
        selected_topics=body.selected_topics if body.scope == "topic" else None,
        difficulty=body.difficulty,
        use_pyq_reference=body.use_pyq_reference,
        types_ratio={
            "MCQ": body.types_ratio.MCQ,
            "MSQ": body.types_ratio.MSQ,
            "NAT": body.types_ratio.NAT,
        },
        total_questions=65,
        total_marks=100,
        duration_minutes=180,
        question_ids=[],
        question_order=[],
        status="generating",
        generation_progress={"total": 65, "completed": 0, "failed": 0},
    )
    db.add(exam)
    await db.commit()

    # ── 6. Kick off background generation ──
    asyncio.create_task(run_generation(exam_id))

    return ExamGenerateResponse(
        exam_id=exam.id,
        status=exam.status,
        message="Exam generation started. Poll GET /exams/{id}/status for progress.",
    )


# ── GET /exams ────────────────────────────────────────────────────────────────

@router.get(
    "",
    response_model=ExamHistoryResponse,
    summary="List exams for the current user with pagination",
)
async def list_exams(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Exam)
        .where(Exam.user_id == user.id)
        .order_by(Exam.created_at.desc())
    )
    exams = result.scalars().all()

    total = len(exams)
    start = (page - 1) * page_size
    end = start + page_size
    page_exams = exams[start:end]

    exam_ids = [exam.id for exam in page_exams]
    attempts_by_exam: dict[str, Attempt] = {}

    if exam_ids:
        attempts_result = await db.execute(
            select(Attempt)
            .where(
                Attempt.exam_id.in_(exam_ids),
                Attempt.user_id == user.id,
            )
            .order_by(Attempt.created_at.desc())
        )
        for attempt in attempts_result.scalars().all():
            exam_id = str(attempt.exam_id)
            if exam_id not in attempts_by_exam:
                attempts_by_exam[exam_id] = attempt

    return ExamHistoryResponse(
        items=[
            ExamHistoryItem(
                id=exam.id,
                paper=exam.paper,
                scope=exam.scope,
                selected_topics=exam.selected_topics,
                difficulty=exam.difficulty,
                total_questions=exam.total_questions,
                total_marks=exam.total_marks,
                duration_minutes=exam.duration_minutes,
                status=exam.status,
                score=(
                    round(float(attempts_by_exam[str(exam.id)].score), 2)
                    if str(exam.id) in attempts_by_exam
                    and attempts_by_exam[str(exam.id)].score is not None
                    else None
                ),
                max_score=(
                    attempts_by_exam[str(exam.id)].max_score
                    if str(exam.id) in attempts_by_exam
                    else exam.total_marks
                ),
                attempt_id=(
                    str(attempts_by_exam[str(exam.id)].id)
                    if str(exam.id) in attempts_by_exam
                    else None
                ),
                created_at=exam.created_at,
            )
            for exam in page_exams
        ],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=ceil(total / page_size) if total > 0 else 0,
    )


# ── GET /exams/{exam_id}/status ───────────────────────────────────────────────

@router.get(
    "/{exam_id}/status",
    summary="Poll exam generation progress",
)
async def get_exam_status(
    exam_id: uuid_module.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Exam).where(Exam.id == exam_id, Exam.user_id == user.id)
    )
    exam = result.scalar_one_or_none()
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")

    progress = exam.generation_progress or {}
    return {
        "exam_id": str(exam.id),
        "status": exam.status,
        "progress": {
            "total": progress.get("total", 65),
            "completed": progress.get("completed", 0),
            "failed": progress.get("failed", 0),
            "batch": progress.get("batch"),
            "error": progress.get("error"),
        },
    }


# ── POST /exams/{exam_id}/start ───────────────────────────────────────────────

@router.post(
    "/{exam_id}/start",
    response_model=AttemptStartResponse,
    summary="Start or resume an exam attempt",
)
async def start_exam(
    exam_id: uuid_module.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Creates a new attempt for the exam, or resumes an existing in-progress one.
    Records server-side start_time for the authoritative timer.
    Returns the attempt with any previously saved responses (for resume).
    """
    # ── 1. Get exam ──
    result = await db.execute(
        select(Exam).where(Exam.id == exam_id, Exam.user_id == user.id)
    )
    exam = result.scalar_one_or_none()
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")

    if exam.status == "generating":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exam is still being generated. Please wait.",
        )
    if exam.status == "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exam generation failed. Please generate a new exam.",
        )
    if exam.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This exam has already been completed.",
        )
    if exam.status not in ("generated", "in_progress"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot start exam with status '{exam.status}'.",
        )

    now = datetime.now(timezone.utc)
    duration_seconds = exam.duration_minutes * 60

    # ── 2. Check for existing in-progress attempt (resume) ──
    existing_result = await db.execute(
        select(Attempt).where(
            Attempt.exam_id == exam_id,
            Attempt.user_id == user.id,
            Attempt.submitted == False,  # noqa: E712
        )
    )
    existing = existing_result.scalar_one_or_none()

    if existing is not None:
        # Resume existing attempt
        elapsed = (now - existing.start_time).total_seconds()
        remaining = max(0, duration_seconds - int(elapsed))

        if remaining <= 0:
            # Time has expired — auto-submit AND grade so the attempt has a
            # real score (grade_attempt sets submitted/end_time, marks the exam
            # completed, and commits).
            existing.auto_submitted = True
            await grade_attempt(db, str(existing.id))
            await refresh_user_analytics_safely(db, user.id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exam time has expired. The attempt has been auto-submitted.",
            )

        return AttemptStartResponse(
            attempt_id=str(existing.id),
            exam_id=str(exam.id),
            start_time=existing.start_time.isoformat(),
            remaining_seconds=remaining,
            responses=existing.responses or {},
            question_statuses=existing.question_statuses or {},
            submitted=existing.submitted,
            is_resume=True,
        )

    # ── 3. Create new attempt ──
    attempt = Attempt(
        id=uuid_module.uuid4(),
        exam_id=exam.id,
        user_id=user.id,
        start_time=now,
        submitted=False,
        auto_submitted=False,
        responses={},
        question_statuses={},
        events_log=[],
        max_score=exam.total_marks,
    )
    db.add(attempt)

    # Update exam status to in_progress
    exam.status = "in_progress"
    await db.commit()

    return AttemptStartResponse(
        attempt_id=str(attempt.id),
        exam_id=str(exam.id),
        start_time=now.isoformat(),
        remaining_seconds=duration_seconds,
        responses={},
        question_statuses={},
        submitted=False,
        is_resume=False,
    )


# ── GET /exams/{exam_id} ──────────────────────────────────────────────────────

@router.get(
    "/{exam_id}",
    response_model=ExamScreenResponse,
    summary="Get exam questions for the exam screen (NO answers)",
)
async def get_exam(
    exam_id: uuid_module.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns the exam with all questions in order, but WITHOUT correct answers.
    Used by the exam screen to render questions.
    """
    # ── 1. Get exam ──
    result = await db.execute(
        select(Exam).where(Exam.id == exam_id, Exam.user_id == user.id)
    )
    exam = result.scalar_one_or_none()
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")

    if exam.status == "generating":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exam is still being generated.",
        )
    if exam.status == "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exam generation failed.",
        )
    if not exam.question_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exam has no questions assembled yet.",
        )

    # ── 2. Build question_id → order_entry map ──
    # Newly generated exams always carry valid question_id values in
    # question_order. Legacy exams generated before that fix may still have
    # empty question_id strings stored in the DB, so fall back to
    # exam.question_ids if question_order yields no valid IDs.
    question_order: list[dict] = exam.question_order or []
    id_to_order: dict[str, dict] = {
        str(entry["question_id"]): entry
        for entry in question_order
        if entry.get("question_id")
    }

    # Use exam.question_ids as source of truth if id_to_order is empty
    if not id_to_order and exam.question_ids:
        for i, qid in enumerate(exam.question_ids):
            id_to_order[str(qid)] = {"qno": i + 1, "section": "Subject"}

    # ── 3. Fetch questions from question_bank ──
    valid_ids = list(id_to_order.keys())
    if not valid_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No valid question IDs found in this exam.",
        )

    # Convert string UUIDs to uuid objects for SQLAlchemy query
    uuid_ids = []
    for qid in valid_ids:
        try:
            uuid_ids.append(uuid_module.UUID(qid))
        except ValueError:
            pass

    if not uuid_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No valid UUIDs to query questions.",
        )

    qb_result = await db.execute(
        select(QuestionBank).where(QuestionBank.id.in_(uuid_ids))
    )
    questions_map: dict[str, QuestionBank] = {
        str(q.id): q for q in qb_result.scalars().all()
    }

    # ── 4. Build ordered list without answers ──
    questions: list[QuestionItem] = []
    for qid_str in valid_ids:
        entry = id_to_order[qid_str]
        q = questions_map.get(qid_str)
        if not q:
            continue

        questions.append(
            QuestionItem(
                id=str(q.id),
                qno=entry.get("qno", 0),
                question_type=q.question_type,
                marks=q.marks,
                section=entry.get("section", "Subject"),
                section_name=q.section_name,
                topic=q.topic,
                stem_tex=q.stem_tex,
                code_snippet=q.code_snippet,
                code_language=q.code_language,
                choices=q.choices,
                estimated_time_seconds=q.estimated_time_seconds,
                # NOTE: answer is intentionally excluded
            )
        )

    return ExamScreenResponse(
        exam_id=str(exam.id),
        paper=exam.paper,
        difficulty=exam.difficulty,
        total_questions=exam.total_questions,
        total_marks=exam.total_marks,
        duration_minutes=exam.duration_minutes,
        questions=questions,
    )


# ── DELETE /exams/{exam_id} ───────────────────────────────────────────────────

@router.delete(
    "/{exam_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an exam",
)
async def delete_exam(
    exam_id: uuid_module.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Exam).where(Exam.id == exam_id, Exam.user_id == user.id)
    )
    exam = result.scalar_one_or_none()
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found.")

    await db.delete(exam)
    await db.commit()
