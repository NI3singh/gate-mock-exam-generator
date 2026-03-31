from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.dashboard import DashboardStats
from app.services.analytics_service import get_dashboard_summary as fetch_dashboard_summary

router = APIRouter()


@router.get(
    "/summary",
    response_model=DashboardStats,
    summary="Get dashboard summary for the current user",
)
async def get_dashboard_summary(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await fetch_dashboard_summary(db, user.id)
