from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.syllabus import Syllabus
from app.schemas.syllabus import (
    SyllabusResponse,
    SyllabusSection,
    TopicItem,
    TopicListResponse,
    TopicFlat,
)

router = APIRouter()

VALID_PAPERS = {"CS", "DA", "GA"}


def _validate_paper(paper: str) -> str:
    """Normalise to uppercase and validate."""
    paper = paper.upper()
    if paper not in VALID_PAPERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid paper '{paper}'. Must be one of: {', '.join(sorted(VALID_PAPERS))}",
        )
    return paper


@router.get(
    "/{paper}",
    response_model=SyllabusResponse,
    summary="Get syllabus for a paper, grouped by sections",
)
async def get_syllabus(
    paper: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns the full syllabus taxonomy for CS, DA, or GA,
    organised as sections → topics.
    """
    paper = _validate_paper(paper)

    result = await db.execute(
        select(Syllabus)
        .where(Syllabus.paper == paper)
        .order_by(Syllabus.section_name, Syllabus.id)
    )
    rows = result.scalars().all()

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No syllabus data found for paper '{paper}'. "
            "Have you called POST /api/v1/admin/load-data ?",
        )

    # Group by section_name preserving insertion order
    sections_map: dict[str, list[TopicItem]] = {}
    for row in rows:
        if row.section_name not in sections_map:
            sections_map[row.section_name] = []
        sections_map[row.section_name].append(
            TopicItem(id=row.id, topic=row.topic, subtopic=row.subtopic)
        )

    sections = [
        SyllabusSection(section_name=name, topics=topics)
        for name, topics in sections_map.items()
    ]

    return SyllabusResponse(
        paper=paper,
        total_topics=len(rows),
        sections=sections,
    )


@router.get(
    "/{paper}/topics",
    response_model=TopicListResponse,
    summary="Get flat list of topics for a paper",
)
async def get_topics(
    paper: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns a flat list of all topics for a paper.
    Used by the frontend exam-configuration page
    to render topic-selection checkboxes.
    """
    paper = _validate_paper(paper)

    result = await db.execute(
        select(Syllabus)
        .where(Syllabus.paper == paper)
        .order_by(Syllabus.section_name, Syllabus.id)
    )
    rows = result.scalars().all()

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No syllabus data found for paper '{paper}'. "
            "Have you called POST /api/v1/admin/load-data ?",
        )

    topics = [
        TopicFlat(id=row.id, section_name=row.section_name, topic=row.topic)
        for row in rows
    ]

    return TopicListResponse(
        paper=paper,
        total_topics=len(topics),
        topics=topics,
    )