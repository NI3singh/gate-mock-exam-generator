"""
Central LLM configuration constants.
"""

from app.core.config import settings

LLM_CONFIG = {
    "provider": settings.LLM_PROVIDER,
    "max_tokens": settings.LLM_MAX_TOKENS,
    "temperature": settings.LLM_TEMPERATURE,
    "temperature_verify": settings.LLM_TEMPERATURE_VERIFY,
    "batch_size": settings.LLM_BATCH_SIZE,
    "max_concurrency": settings.LLM_MAX_CONCURRENCY,
    "retries": settings.LLM_RETRIES,
    "timeout_seconds": settings.LLM_TIMEOUT_SECONDS,
}

# GATE exam structure constants
GATE_TOTAL_QUESTIONS = 65
GATE_TOTAL_MARKS = 100
GATE_DURATION_MINUTES = 180

GA_QUESTIONS = 10
GA_MARKS = 15
GA_1MARK = 5
GA_2MARK = 5

SUBJECT_QUESTIONS = 55
SUBJECT_MARKS = 85
SUBJECT_1MARK = 25
SUBJECT_2MARK = 30
