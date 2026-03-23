"""
Wrapper around the Nebius API (OpenAI-compatible) for LLM calls.
"""

import asyncio
import json
import logging
import re

from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

# ── Async semaphore to limit concurrent LLM calls ──
_llm_semaphore = asyncio.Semaphore(2)

# ── Lazy-initialised client ──
_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            base_url=settings.NEBIUS_BASE_URL,
            api_key=settings.NEBIUS_API_KEY,
        )
    return _client


async def call_llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float | None = None,
    max_tokens: int | None = None,
    retries: int = 2,
) -> str:
    """
    Call the LLM with rate-limiting (semaphore) and retry logic.
    Returns the raw text content from the LLM response.
    """
    client = _get_client()
    temp = temperature if temperature is not None else settings.LLM_TEMPERATURE
    tokens = max_tokens if max_tokens is not None else settings.LLM_MAX_TOKENS

    last_error: Exception | None = None

    for attempt in range(1, retries + 2):  # retries + 1 total attempts
        try:
            async with _llm_semaphore:
                logger.info(f"LLM call attempt {attempt} (temp={temp})")

                response = await client.chat.completions.create(
                    model=settings.NEBIUS_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=temp,
                    max_tokens=tokens,
                )

                content = response.choices[0].message.content
                if not content:
                    raise ValueError("LLM returned empty content")

                logger.info(
                    f"LLM call successful (tokens: "
                    f"in={response.usage.prompt_tokens}, "
                    f"out={response.usage.completion_tokens})"
                )
                return content

        except Exception as exc:
            last_error = exc
            logger.warning(f"LLM call attempt {attempt} failed: {exc}")
            if attempt <= retries:
                wait = 2 ** attempt  # exponential backoff: 2, 4 seconds
                logger.info(f"Retrying in {wait}s...")
                await asyncio.sleep(wait)

    raise RuntimeError(
        f"LLM call failed after {retries + 1} attempts: {last_error}"
    )


def extract_json_array(text: str) -> list[dict]:
    """
    Extract a JSON array from LLM response text.
    Handles markdown code fences and extra surrounding text.
    """
    cleaned = text.strip()

    # 1. Try markdown code fence: ```json ... ``` or ``` ... ```
    fence_pattern = r"```(?:json)?\s*\n?(.*?)\n?\s*```"
    match = re.search(fence_pattern, cleaned, re.DOTALL)
    if match:
        cleaned = match.group(1).strip()

    # 2. Find the outermost [ ... ]
    start = cleaned.find("[")
    end = cleaned.rfind("]")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start : end + 1]

    # 3. Parse JSON
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.error(f"JSON parse error: {exc}\nRaw text:\n{text[:500]}")
        raise ValueError(f"Failed to parse LLM response as JSON: {exc}")

    if not isinstance(parsed, list):
        raise ValueError(f"Expected JSON array, got {type(parsed).__name__}")

    return parsed