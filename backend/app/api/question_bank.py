from math import ceil

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.question_bank import QuestionBank
from app.models.user import User
from app.schemas.question_bank import (
    QuestionBankBrowserItem,
    QuestionBankBrowserResponse,
)

router = APIRouter()


@router.get(
    "",
    response_model=QuestionBankBrowserResponse,
    summary="Browse question bank with filters",
)
async def browse_question_bank(
    paper: str | None = Query(default=None),
    topic: str | None = Query(default=None),
    difficulty: str | None = Query(default=None),
    question_type: str | None = Query(default=None, alias="type"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=50),
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    filters = []

    if paper:
        filters.append(QuestionBank.paper == paper.upper())
    if topic:
        filters.append(QuestionBank.topic.ilike(f"%{topic.strip()}%"))
    if difficulty:
        filters.append(QuestionBank.difficulty == difficulty.lower())
    if question_type:
        filters.append(QuestionBank.question_type == question_type.upper())

    total_query = select(func.count()).select_from(QuestionBank)
    items_query = select(QuestionBank)

    if filters:
        total_query = total_query.where(*filters)
        items_query = items_query.where(*filters)

    total_result = await db.execute(total_query)
    total = int(total_result.scalar() or 0)

    offset = (page - 1) * page_size
    items_result = await db.execute(
        items_query.order_by(QuestionBank.generated_at.desc()).offset(offset).limit(page_size)
    )
    questions = items_result.scalars().all()

    return QuestionBankBrowserResponse(
        items=[
            QuestionBankBrowserItem(
                id=str(question.id),
                paper=question.paper,
                question_type=question.question_type,
                marks=question.marks,
                difficulty=question.difficulty,
                section_name=question.section_name,
                topic=question.topic,
                stem_tex=question.stem_tex,
                code_snippet=question.code_snippet,
                code_language=question.code_language,
                choices=question.choices,
                answer=question.answer,
                solution_tex=question.solution_tex,
                estimated_time_seconds=question.estimated_time_seconds,
                generated_at=question.generated_at,
            )
            for question in questions
        ],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=ceil(total / page_size) if total > 0 else 0,
    )
