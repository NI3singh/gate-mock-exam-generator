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
    If the row is missing in PostgreSQL but the Firebase token is valid,
    lazily create it so the same Firebase account works across environments.
    """
    firebase_uid: str = decoded["uid"]
    email: str = decoded.get("email", "")
    display_name: str | None = decoded.get("name")

    result = await db.execute(
        select(User).where(User.firebase_uid == firebase_uid)
    )
    user = result.scalar_one_or_none()

    if user is None:
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Firebase token is missing the user's email claim.",
            )

        user = User(
            firebase_uid=firebase_uid,
            email=email,
            display_name=display_name,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    updated = False

    if email and user.email != email:
        user.email = email
        updated = True

    if display_name and not user.display_name:
        user.display_name = display_name
        updated = True

    if updated:
        await db.commit()
        await db.refresh(user)

    return user
