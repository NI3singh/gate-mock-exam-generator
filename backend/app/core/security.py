"""
FastAPI dependencies for authentication / authorisation.

Two granularity levels:
  • verify_firebase_token  – just validates the JWT, returns decoded claims
  • get_current_user       – validates JWT *and* fetches the User row from PG
"""

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core import firebase_auth
from app.models.user import User


async def verify_firebase_token(request: Request) -> dict:
    """
    Extract the Bearer token from the Authorization header,
    verify it with Firebase, and return the decoded claims.
    Used by the /auth/register endpoint (user may not exist in PG yet).
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header. Expected 'Bearer <token>'.",
        )

    token = auth_header.split("Bearer ", 1)[1]

    try:
        decoded = firebase_auth.verify_id_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )

    return decoded


async def get_current_user(
    decoded: dict = Depends(verify_firebase_token),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Look up the User row that matches the Firebase UID from the JWT.
    Returns 401 if the user has not called /auth/register yet.
    """
    firebase_uid: str = decoded["uid"]

    result = await db.execute(
        select(User).where(User.firebase_uid == firebase_uid)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not registered. Please call POST /api/v1/auth/register first.",
        )

    return user