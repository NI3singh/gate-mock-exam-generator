from datetime import datetime, timezone
import io

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.attempt import Attempt
from app.schemas.attempt import (
    AttemptSaveRequest,
    AttemptSaveResponse,
    AttemptEventRequest,
    AttemptEventResponse,
    AttemptSubmitResponse,
    AttemptDetailResponse,
)
from app.services.grading_engine import grade_attempt
from app.services.attempt_detail_service import build_attempt_detail

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
    try:
        return await build_attempt_detail(db, attempt_id, user.id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
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


# ── GET /attempts/{attempt_id}/solutions-pdf ──────────────────────────────────


@router.get(
    "/{attempt_id}/solutions-pdf",
    summary="Download full solution key as PDF",
)
async def download_solutions_pdf(
    attempt_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generates a full question-by-question solution key PDF using the
    LaTeX.online compile API and serves the cached file for download.
    """
    from app.services.pdf_service import generate_solutions_pdf

    try:
        pdf_path = await generate_solutions_pdf(db, attempt_id, user.id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Solution PDF generation failed: {exc}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected PDF error: {exc}",
        )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"GATE2026_Solution_Key_{attempt_id}.pdf",
    )
