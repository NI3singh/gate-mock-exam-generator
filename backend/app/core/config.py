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

    # Nebius LLM
    NEBIUS_API_KEY: str = os.getenv("NEBIUS_API_KEY", "")

    NEBIUS_BASE_URL: str = os.getenv(
    "NEBIUS_BASE_URL", "https://api.studio.nebius.com/v1/"
    )
    NEBIUS_MODEL: str = os.getenv("NEBIUS_MODEL", "google/gemma-3-27b-it")

    # LLM defaults
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "16000"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_TEMPERATURE_VERIFY: float = float(os.getenv("LLM_TEMPERATURE_VERIFY", "0.1"))
    LLM_BATCH_SIZE: int = int(os.getenv("LLM_BATCH_SIZE", "5"))


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