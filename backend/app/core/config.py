import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the backend root directory
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/gate_mock_test",
    )

    # Firebase
    FIREBASE_SERVICE_ACCOUNT_PATH: str = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT_PATH", "./firebase-service-account.json"
    )

    # App
    APP_ENV: str = os.getenv("APP_ENV", "development")

    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
        ).split(",")
    ]

    # In development allow everything so ngrok just works
    if APP_ENV == "development":
        CORS_ORIGINS = ["*"]


settings = Settings()