from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.user import User
from app.schemas.dashboard import DashboardStats

router = APIRouter()


@router.get(
    "/summary",
    response_model=DashboardStats,
    summary="Get dashboard summary for the current user",
)
async def get_dashboard_summary(
    user: User = Depends(get_current_user),
):
    """
    Returns aggregated stats and recent exams for the logged-in user.

    Right now this returns defaults (zeros / empty list) because the
    exams and attempts tables don't exist yet.  When Part 3+ is built
    this will query real data.
    """
    # ── Will be replaced with real queries once exam tables exist ──
    return DashboardStats(
        total_exams_taken=0,
        average_score=None,
        best_score=None,
        worst_score=None,
        total_questions_attempted=0,
        recent_exams=[],
    )