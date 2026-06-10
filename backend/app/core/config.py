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

    # OpenAI / OpenAI-compatible LLM (set OPENAI_BASE_URL to use a gateway
    # such as tokenlb.net; leave it blank to hit the real OpenAI API).
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "")

    # Anthropic LLM
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "")

    # LLM defaults
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "16000"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_TEMPERATURE_VERIFY: float = float(os.getenv("LLM_TEMPERATURE_VERIFY", "0.1"))
    LLM_BATCH_SIZE: int = int(os.getenv("LLM_BATCH_SIZE", "5"))
    LLM_MAX_CONCURRENCY: int = int(os.getenv("LLM_MAX_CONCURRENCY", "2"))
    LLM_RETRIES: int = int(os.getenv("LLM_RETRIES", "2"))
    LLM_TIMEOUT_SECONDS: int = int(os.getenv("LLM_TIMEOUT_SECONDS", "120"))

    # Generation resilience.
    # LLM_GEN_MAX_SECONDS is a HARD ceiling on a single exam's whole generation
    # run (concurrent first pass + every top-up round). LLM_TOPUP_* bound the
    # self-healing top-up phase. INVARIANT: keep LLM_TOPUP_TIME_BUDGET_SECONDS
    # comfortably BELOW LLM_GEN_MAX_SECONDS so top-up exits via its own soft
    # budget instead of being cancelled mid-DB-write by the hard timeout.
    LLM_GEN_MAX_SECONDS: int = int(os.getenv("LLM_GEN_MAX_SECONDS", "900"))
    LLM_TOPUP_MAX_ROUNDS: int = int(os.getenv("LLM_TOPUP_MAX_ROUNDS", "3"))
    LLM_TOPUP_TIME_BUDGET_SECONDS: int = int(
        os.getenv("LLM_TOPUP_TIME_BUDGET_SECONDS", "420")
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
