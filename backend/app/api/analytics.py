from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.analytics import AnalyticsDashboardResponse, TopicPerformanceResponse
from app.services.analytics_service import (
    get_analytics_dashboard,
    get_topic_performance,
)

router = APIRouter()


@router.get(
    "/dashboard",
    response_model=AnalyticsDashboardResponse,
    summary="Get analytics dashboard for the current user",
)
async def analytics_dashboard(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_analytics_dashboard(db, user.id)


@router.get(
    "/topic-performance",
    response_model=TopicPerformanceResponse,
    summary="Get topic-wise performance for the current user",
)
async def analytics_topic_performance(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_topic_performance(db, user.id)
