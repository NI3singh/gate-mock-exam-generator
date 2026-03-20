from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.syllabus import DataLoadResponse, SyllabusStatsResponse
from app.services.data_loader import load_syllabus, get_syllabus_stats

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
    Reads syllabus JSONs from backend/data/syllabus/ and inserts into
    the `syllabus` table.  Idempotent — safe to call multiple times.

    Requires authentication (any logged-in user can trigger this for now).
    """
    result = await load_syllabus(db)

    if result.errors and not result.papers_loaded:
        message = "Data loading failed — see errors"
    elif result.errors:
        message = "Data partially loaded — some files had errors"
    else:
        message = "All syllabus data loaded successfully"

    return DataLoadResponse(
        message=message,
        papers_loaded=result.papers_loaded,
        total_rows_inserted=result.total_rows_inserted,
        details=result.details,
        errors=result.errors,
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
    """Returns counts of topics per paper currently in the database."""
    stats = await get_syllabus_stats(db)
    return SyllabusStatsResponse(stats=stats)