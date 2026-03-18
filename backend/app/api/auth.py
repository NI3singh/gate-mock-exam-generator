from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, verify_firebase_token
from app.models.user import User
from app.schemas.auth import RegisterRequest, UpdateProfileRequest, UserResponse

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user after Firebase signup",
)
async def register(
    body: RegisterRequest,
    decoded: dict = Depends(verify_firebase_token),
    db: AsyncSession = Depends(get_db),
):
    """
    Called once right after the client creates a Firebase account.
    Idempotent — if the user already exists, returns the existing row.
    """
    firebase_uid: str = decoded["uid"]
    email: str = decoded.get("email", "")

    # Check if already registered
    result = await db.execute(
        select(User).where(User.firebase_uid == firebase_uid)
    )
    existing = result.scalar_one_or_none()
    if existing is not None:
        return existing

    user = User(
        firebase_uid=firebase_uid,
        email=email,
        display_name=body.display_name,
        preferred_paper=body.preferred_paper,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_me(
    user: User = Depends(get_current_user),
):
    return user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
)
async def update_me(
    body: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.display_name is not None:
        user.display_name = body.display_name
    if body.preferred_paper is not None:
        user.preferred_paper = body.preferred_paper

    await db.commit()
    await db.refresh(user)
    return user