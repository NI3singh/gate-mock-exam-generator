from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.syllabus import DataLoadResponse, SyllabusStatsResponse
from app.services.data_loader import (
    load_syllabus,
    load_pyqs,
    get_syllabus_stats,
    get_pyq_stats,
)

router = APIRouter()


@router.post(
    "/load-data",
    response_model=DataLoadResponse,
    summary="Load syllabus JSON files into the database",
)
async def load_data(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Reads syllabus JSONs from backend/data/syllabus/ and PYQ JSONs from
    backend/data/pyqs/ (optional) and inserts into the `syllabus` and
    `pyq_questions` tables.  Idempotent — safe to call multiple times.

    Requires authentication (any logged-in user can trigger this for now).
    """
    syllabus_result = await load_syllabus(db)
    pyq_result = await load_pyqs(db)

    papers_loaded = syllabus_result.papers_loaded + pyq_result.papers_loaded
    errors = syllabus_result.errors + pyq_result.errors

    if errors and not papers_loaded:
        message = "Data loading failed — see errors"
    elif errors:
        message = "Data partially loaded — some files had errors"
    else:
        message = "All data loaded successfully"

    return DataLoadResponse(
        message=message,
        papers_loaded=papers_loaded,
        total_rows_inserted=(
            syllabus_result.total_rows_inserted + pyq_result.total_rows_inserted
        ),
        details={**syllabus_result.details, **pyq_result.details},
        errors=errors,
    )


@router.get(
    "/data-stats",
    response_model=SyllabusStatsResponse,
    summary="Get current data loading status",
)
async def data_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns counts of topics and PYQs per paper currently in the database."""
    stats = await get_syllabus_stats(db)
    stats["pyqs"] = await get_pyq_stats(db)
    return SyllabusStatsResponse(stats=stats)