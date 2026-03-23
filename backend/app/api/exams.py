import asyncio
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.exam import Exam
from app.models.syllabus import Syllabus
from app.schemas.exam import ExamGenerateRequest, ExamGenerateResponse, ExamSummary
from app.services.question_generator import run_generation

router = APIRouter()


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
    """
    Validates the exam configuration, creates an exam row with
    status 'generating', kicks off background generation, and returns exam_id.
    """

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

    # ── 3. If scope is 'topic', validate selected_topics ──
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
    exam_id = uuid.uuid4()

    exam = Exam(
        id=exam_id,
        user_id=user.id,
        paper=body.paper,
        scope=body.scope,
        selected_topics=body.selected_topics if body.scope == "topic" else None,
        difficulty=body.difficulty,
        use_pyq_reference=False,
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


@router.get(
    "",
    response_model=list[ExamSummary],
    summary="List all exams for the current user",
)
async def list_exams(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns all exams created by the current user, newest first."""
    result = await db.execute(
        select(Exam)
        .where(Exam.user_id == user.id)
        .order_by(Exam.created_at.desc())
    )
    exams = result.scalars().all()

    return [
        ExamSummary(
            id=e.id,
            paper=e.paper,
            scope=e.scope,
            selected_topics=e.selected_topics,
            difficulty=e.difficulty,
            total_questions=e.total_questions,
            total_marks=e.total_marks,
            duration_minutes=e.duration_minutes,
            status=e.status,
            created_at=e.created_at,
        )
        for e in exams
    ]


@router.get(
    "/{exam_id}/status",
    summary="Poll exam generation progress",
)
async def get_exam_status(
    exam_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns current generation status and progress.
    Frontend polls this every 3 seconds during generation.
    """
    result = await db.execute(
        select(Exam).where(Exam.id == exam_id, Exam.user_id == user.id)
    )
    exam = result.scalar_one_or_none()

    if exam is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found.",
        )

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


@router.delete(
    "/{exam_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an exam",
)
async def delete_exam(
    exam_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an exam and its associated data."""
    result = await db.execute(
        select(Exam).where(Exam.id == exam_id, Exam.user_id == user.id)
    )
    exam = result.scalar_one_or_none()

    if exam is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found.",
        )

    await db.delete(exam)
    await db.commit()