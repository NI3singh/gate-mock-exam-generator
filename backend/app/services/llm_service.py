"""
Provider-neutral LLM service used by the exam generation pipeline.
"""

import asyncio
import json
import logging
import re

from app.core.config import settings
from app.services.llm.registry import get_active_provider
from app.services.llm.types import LLMRequest

logger = logging.getLogger(__name__)

# Limit concurrent provider calls from this backend process.
_llm_semaphore = asyncio.Semaphore(max(1, settings.LLM_MAX_CONCURRENCY))


def get_active_llm_metadata() -> dict[str, str]:
    """Return provider/model metadata for storing generated questions."""
    provider = get_active_provider()
    return {
        "provider": provider.name,
        "model": provider.model,
    }


async def call_llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float | None = None,
    max_tokens: int | None = None,
    retries: int = settings.LLM_RETRIES,
) -> str:
    """
    Call the active LLM provider with rate-limiting, timeout, and retry logic.
    Returns the raw text content from the LLM response.
    """
    provider = get_active_provider()
    temp = temperature if temperature is not None else settings.LLM_TEMPERATURE
    tokens = max_tokens if max_tokens is not None else settings.LLM_MAX_TOKENS
    request = LLMRequest(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=temp,
        max_tokens=tokens,
    )

    last_error: Exception | None = None

    for attempt in range(1, retries + 2):  # retries + 1 total attempts
        try:
            async with _llm_semaphore:
                logger.info(
                    "LLM call attempt %s provider=%s model=%s temp=%s max_tokens=%s",
                    attempt,
                    provider.name,
                    provider.model,
                    temp,
                    tokens,
                )

                response = await asyncio.wait_for(
                    provider.generate(request),
                    timeout=settings.LLM_TIMEOUT_SECONDS,
                )

                if not response.text:
                    raise ValueError("LLM returned empty content")

                usage = response.usage or {}
                logger.info(
                    "LLM call successful provider=%s model=%s tokens_in=%s "
                    "tokens_out=%s",
                    response.provider,
                    response.model,
                    usage.get("prompt_tokens"),
                    usage.get("completion_tokens"),
                )
                return response.text

        except Exception as exc:
            last_error = exc
            logger.warning(
                "LLM call attempt %s failed provider=%s model=%s error=%s",
                attempt,
                provider.name,
                provider.model,
                exc,
            )
            if attempt <= retries:
                wait = 2 ** attempt
                logger.info("Retrying in %ss...", wait)
                await asyncio.sleep(wait)

    raise RuntimeError(
        "LLM call failed after "
        f"{retries + 1} attempts "
        f"(provider={provider.name}, model={provider.model}): {last_error}"
    )


def _fix_json_latex_escapes(text: str) -> str:
    """
    Character-by-character fix for unescaped LaTeX backslashes inside JSON strings.

    LLMs frequently output LaTeX commands with single backslashes inside JSON,
    e.g.: \\pi, \\frac, \\sigma, \\mathbb, \\nabla, \\texttt, \\{, \\}.
    These are invalid JSON escape sequences and cause json.loads to fail.

    JSON only allows these escape sequences:
        \\"  \\\\  \\/  \\b  \\f  \\n  \\r  \\t  \\uXXXX

    Strategy: walk character-by-character, track whether we are inside a JSON
    string, and whenever we see a backslash that starts an invalid escape,
    double it.
    """
    result = []
    i = 0
    in_string = False

    while i < len(text):
        c = text[i]

        if not in_string:
            result.append(c)
            if c == '"':
                in_string = True
            i += 1
            continue

        if c == '"':
            in_string = False
            result.append(c)
            i += 1
            continue

        if c != "\\":
            result.append(c)
            i += 1
            continue

        if i + 1 >= len(text):
            result.append(c)
            i += 1
            continue

        nxt = text[i + 1]

        if nxt in '"\\/':
            result.append(c)
            result.append(nxt)
            i += 2
            continue

        if nxt == "u":
            hex_chars = text[i + 2: i + 6]
            if len(hex_chars) == 4 and all(
                h in "0123456789abcdefABCDEF" for h in hex_chars
            ):
                result.append(c)
                result.append(nxt)
                i += 2
                continue
            result.append("\\")
            result.append("\\")
            i += 1
            continue

        if nxt in "bfnrt":
            after_nxt = text[i + 2] if i + 2 < len(text) else ""
            if after_nxt.isalpha():
                result.append("\\")
                result.append("\\")
                i += 1
            else:
                result.append(c)
                result.append(nxt)
                i += 2
            continue

        result.append("\\")
        result.append("\\")
        i += 1

    return "".join(result)


def extract_json_array(text: str) -> list[dict]:
    """
    Extract a JSON array from LLM response text.

    Steps:
      1. Strip markdown code fences if present.
      2. Find the outermost [ ... ] array.
      3. Fix any unescaped LaTeX backslashes.
      4. Parse JSON and return.
    """
    cleaned = text.strip()

    fence_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", cleaned, re.DOTALL)
    if fence_match:
        cleaned = fence_match.group(1).strip()

    start = cleaned.find("[")
    end = cleaned.rfind("]")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start: end + 1]

    fixed = _fix_json_latex_escapes(cleaned)

    try:
        parsed = json.loads(fixed)
    except json.JSONDecodeError as exc:
        logger.error(
            "JSON parse error after escape-fix: %s\n"
            "--- Original LLM text (first 600 chars) ---\n%s\n"
            "--- Fixed text (first 600 chars) ---\n%s",
            exc,
            text[:600],
            fixed[:600],
        )
        raise ValueError(f"Failed to parse LLM response as JSON: {exc}")

    if not isinstance(parsed, list):
        raise ValueError(f"Expected JSON array, got {type(parsed).__name__}")

    return parsed


def extract_json_object(text: str) -> dict:
    """
    Extract a single JSON object from LLM response text.

    Mirrors extract_json_array: strips code fences, isolates the outermost
    { ... }, repairs unescaped LaTeX backslashes, then parses.
    """
    cleaned = text.strip()

    fence_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", cleaned, re.DOTALL)
    if fence_match:
        cleaned = fence_match.group(1).strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start: end + 1]

    fixed = _fix_json_latex_escapes(cleaned)

    try:
        parsed = json.loads(fixed)
    except json.JSONDecodeError as exc:
        logger.error(
            "JSON object parse error after escape-fix: %s\n"
            "--- Original (first 600 chars) ---\n%s",
            exc,
            text[:600],
        )
        raise ValueError(f"Failed to parse LLM response as JSON object: {exc}")

    if not isinstance(parsed, dict):
        raise ValueError(f"Expected JSON object, got {type(parsed).__name__}")

    return parsed
