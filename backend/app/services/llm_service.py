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


def _fix_json_latex_escapes(text: str) -> str:
    """
    Character-by-character fix for unescaped LaTeX backslashes inside JSON strings.

    LLMs frequently output LaTeX commands with single backslashes inside JSON,
    e.g.:  \\pi  \\frac  \\sigma  \\mathbb  \\nabla  \\texttt  \\{  \\}
    These are INVALID JSON escape sequences and cause json.loads to crash.

    JSON only allows these escape sequences:
        \\"  \\\\  \\/  \\b  \\f  \\n  \\r  \\t  \\uXXXX

    Anything else (\\p, \\m, \\s, \\{, \\J, \\l, etc.) is invalid.
    Also \\f, \\n, \\b, \\r, \\t followed by a letter means a LaTeX command
    (\\frac, \\nabla, \\begin, \\right, \\times) not a JSON control char.

    Strategy: walk character-by-character, track whether we are inside a JSON
    string, and whenever we see a backslash that starts an invalid escape,
    double it.
    """
    result = []
    i = 0
    in_string = False

    while i < len(text):
        c = text[i]

        # ── Outside a JSON string ─────────────────────────────────────────────
        if not in_string:
            result.append(c)
            if c == '"':
                in_string = True
            i += 1
            continue

        # ── Inside a JSON string ──────────────────────────────────────────────
        if c == '"':
            # Unescaped quote ends the string
            in_string = False
            result.append(c)
            i += 1
            continue

        if c != '\\':
            result.append(c)
            i += 1
            continue

        # ── We have a backslash inside a JSON string ──────────────────────────
        if i + 1 >= len(text):
            # Backslash at very end of input — keep as-is
            result.append(c)
            i += 1
            continue

        nxt = text[i + 1]

        # Always-valid JSON escape sequences: \", \\, \/
        if nxt in '"\\/':
            result.append(c)
            result.append(nxt)
            i += 2
            continue

        # Unicode escape \uXXXX — valid only if followed by exactly 4 hex digits
        if nxt == 'u':
            hex_chars = text[i + 2: i + 6]
            if len(hex_chars) == 4 and all(
                h in '0123456789abcdefABCDEF' for h in hex_chars
            ):
                # Valid \uXXXX — keep all 6 chars
                result.append(c)
                result.append(nxt)
                i += 2
                continue
            else:
                # \u NOT followed by 4 hex digits → LaTeX (\underbrace, \uparrow…)
                result.append('\\')
                result.append('\\')
                i += 1
                continue

        # Ambiguous: \b \f \n \r \t
        # These are valid JSON control chars BUT also start many LaTeX commands:
        #   \frac \nabla \begin \right \times \boldsymbol \newline ...
        # Heuristic: if the char AFTER nxt is a letter → it is a LaTeX command.
        #   \frac{  → nxt='f', after='r' (letter) → double backslash
        #   \nabla  → nxt='n', after='a' (letter) → double backslash
        #   "text\n"→ nxt='n', after='"' (not letter) → keep as JSON \n
        if nxt in 'bfnrt':
            after_nxt = text[i + 2] if i + 2 < len(text) else ''
            if after_nxt.isalpha():
                # LaTeX command → double the backslash, don't consume nxt
                result.append('\\')
                result.append('\\')
                i += 1
            else:
                # Legitimate JSON control character
                result.append(c)
                result.append(nxt)
                i += 2
            continue

        # Everything else: \p \m \s \l \a \c \d \{ \} \( \) \^ \_ \| \> \J …
        # All invalid in JSON → double the backslash, leave next char in stream
        result.append('\\')
        result.append('\\')
        i += 1

    return ''.join(result)


def extract_json_array(text: str) -> list[dict]:
    """
    Extract a JSON array from LLM response text.

    Steps:
      1. Strip markdown code fences if present.
      2. Find the outermost [ ... ] array.
      3. Fix any unescaped LaTeX backslashes (character-by-character).
      4. Parse JSON and return.
    """
    cleaned = text.strip()

    # Step 1 — strip ```json ... ``` or ``` ... ``` fences
    fence_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", cleaned, re.DOTALL)
    if fence_match:
        cleaned = fence_match.group(1).strip()

    # Step 2 — find outermost [ ... ]
    start = cleaned.find("[")
    end = cleaned.rfind("]")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start: end + 1]

    # Step 3 — fix LaTeX backslash escaping before parsing
    fixed = _fix_json_latex_escapes(cleaned)

    # Step 4 — parse JSON
    try:
        parsed = json.loads(fixed)
    except json.JSONDecodeError as exc:
        # Log BOTH original and fixed text so we can diagnose remaining issues
        logger.error(
            f"JSON parse error after escape-fix: {exc}\n"
            f"--- Original LLM text (first 600 chars) ---\n{text[:600]}\n"
            f"--- Fixed text (first 600 chars) ---\n{fixed[:600]}"
        )
        raise ValueError(f"Failed to parse LLM response as JSON: {exc}")

    if not isinstance(parsed, list):
        raise ValueError(f"Expected JSON array, got {type(parsed).__name__}")

    return parsed