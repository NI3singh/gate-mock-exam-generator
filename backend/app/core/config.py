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

    # LLM provider selection
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "nebius").strip().lower()

    # Nebius LLM (OpenAI-compatible)
    NEBIUS_API_KEY: str = os.getenv("NEBIUS_API_KEY", "")
    NEBIUS_BASE_URL: str = os.getenv(
        "NEBIUS_BASE_URL", "https://api.studio.nebius.com/v1/"
    )
    NEBIUS_MODEL: str = os.getenv("NEBIUS_MODEL", "deepseek-ai/DeepSeek-V3.2")

    # OpenAI LLM (OPENAI_BASE_URL lets you point at any OpenAI-compatible gateway)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "")

    # Anthropic LLM
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "")

    # Generic LLM credentials - a single fallback that works for ANY provider
    # selected via LLM_PROVIDER. Lets a cloner use a brand-new provider with no
    # new code and no provider-specific env vars:
    #   LLM_PROVIDER=<name>  +  LLM_API_KEY / LLM_MODEL / LLM_BASE_URL
    # Per-provider vars (e.g. NEBIUS_API_KEY) always win over these.
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "")

    # LLM defaults
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "16000"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_TEMPERATURE_VERIFY: float = float(os.getenv("LLM_TEMPERATURE_VERIFY", "0.1"))
    LLM_BATCH_SIZE: int = int(os.getenv("LLM_BATCH_SIZE", "5"))
    LLM_MAX_CONCURRENCY: int = int(os.getenv("LLM_MAX_CONCURRENCY", "2"))
    LLM_RETRIES: int = int(os.getenv("LLM_RETRIES", "2"))
    LLM_TIMEOUT_SECONDS: int = int(os.getenv("LLM_TIMEOUT_SECONDS", "120"))

    # Deficit retry: after the main batch pass, regenerate failed/missing slots.
    GENERATION_DEFICIT_MAX_ROUNDS: int = int(
        os.getenv("GENERATION_DEFICIT_MAX_ROUNDS", "3")
    )
    GENERATION_DEFICIT_BATCH_SIZE: int = int(
        os.getenv("GENERATION_DEFICIT_BATCH_SIZE", "2")
    )
    GENERATION_DEFICIT_ROUND_DELAY_SECONDS: int = int(
        os.getenv("GENERATION_DEFICIT_ROUND_DELAY_SECONDS", "5")
    )

    # PDF / LaTeX
    LATEX_BUILD_URL: str = os.getenv(
        "LATEX_BUILD_URL", "https://latex.ytotech.com/builds/sync"
    )
    LATEX_COMPILER: str = os.getenv("LATEX_COMPILER", "xelatex")

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
