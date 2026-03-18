"""
Thin wrapper around the Firebase Admin SDK.
Initialises the SDK once and exposes a token-verification helper.
"""

import os
from pathlib import Path
from app.core.config import settings

import firebase_admin
from firebase_admin import auth, credentials

_firebase_app = None


def init_firebase() -> None:
    """Call once at application startup (inside lifespan)."""
    global _firebase_app
    if _firebase_app is not None:
        return  # already initialised

    # cred_path = os.getenv(
    #     "FIREBASE_SERVICE_ACCOUNT_PATH", "./firebase-service-account.json"
    # )

    cred_path = settings.FIREBASE_SERVICE_ACCOUNT_PATH
    resolved = Path(cred_path).expanduser().resolve()

    # resolved = Path(cred_path).resolve()
    if not resolved.exists():
        raise FileNotFoundError(
            f"Firebase service-account JSON not found at {resolved}.\n"
            "Download it from Firebase Console → Project Settings → Service Accounts → "
            "Generate New Private Key, then place the file at the path above."
        )

    cred = credentials.Certificate(str(resolved))
    _firebase_app = firebase_admin.initialize_app(cred)


def verify_id_token(token: str) -> dict:
    """
    Verify a Firebase ID-token (JWT) and return the decoded claims dict.
    Raises ``ValueError`` on any verification failure.
    """
    try:
        decoded = auth.verify_id_token(token)
        return decoded
    except firebase_admin.exceptions.FirebaseError as exc:
        raise ValueError(f"Firebase token verification failed: {exc}")
    except Exception as exc:
        raise ValueError(f"Invalid token: {exc}")