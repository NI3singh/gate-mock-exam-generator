"""
Optional LLM verification gate for generated questions.

Disabled by default (settings.LLM_VERIFY_ENABLED). When enabled, each
structurally-valid question is independently re-solved by the LLM; questions
whose answer is judged wrong — or (when LLM_VERIFY_CHECK_DIFFICULTY is on)
whose difficulty/quality is below the GATE bar — are rejected so the
deficit-retry loop regenerates them.

Fail-open: if the verifier call/parse itself errors, the question is KEPT, so a
flaky verifier never silently empties a generation run.
"""

import asyncio
import json
import logging
from pathlib import Path

from app.core.config import settings
from app.services.llm_service import call_llm, extract_json_object

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def _load_prompt(filename: str) -> dict:
    with open(PROMPTS_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


_VERIFY_PROMPT = _load_prompt("verify_answer.json")


def _format_choices(q: dict) -> str:
    choices = q.get("choices")
    if not isinstance(choices, list):
        return "N/A (numeric answer)"
    return "; ".join(f"{chr(65 + i)}) {c}" for i, c in enumerate(choices))


def _format_code_block(q: dict) -> str:
    code = q.get("code_snippet")
    if not code:
        return ""
    lang = q.get("code_language") or ""
    return f"Code ({lang}):\n{code}\n"


async def _verify_one(q: dict, requested_difficulty: str) -> dict | None:
    """Return the verifier verdict dict, or None if verification could not run."""
    user_prompt = _VERIFY_PROMPT["user_prompt_template"].format(
        difficulty=requested_difficulty,
        question_type=q.get("question_type", ""),
        marks=q.get("marks", ""),
        stem_tex=q.get("stem_tex", ""),
        code_block=_format_code_block(q),
        choices=_format_choices(q),
        answer=json.dumps(q.get("answer")),
        solution_tex=q.get("solution_tex", ""),
    )
    try:
        raw = await call_llm(
            system_prompt=_VERIFY_PROMPT["system_prompt"],
            user_prompt=user_prompt,
            temperature=settings.LLM_TEMPERATURE_VERIFY,
        )
        return extract_json_object(raw)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Verification could not run (keeping question): %s", exc)
        return None


def _rejection_reason(verdict: dict) -> str | None:
    """Return a rejection reason string, or None if the question passes."""
    if verdict.get("is_correct") is False:
        return f"incorrect answer: {verdict.get('reason', '')}"[:300]
    if settings.LLM_VERIFY_CHECK_DIFFICULTY and verdict.get("meets_bar") is False:
        return (
            f"below GATE bar (assessed {verdict.get('assessed_difficulty')}): "
            f"{verdict.get('reason', '')}"
        )[:300]
    return None


async def verify_questions(
    questions: list[dict],
    requested_difficulty: str,
) -> tuple[list[dict], list[dict]]:
    """
    Verify a list of structurally-valid questions concurrently.

    Returns (kept, rejected). Callers convert *rejected* into deficit slots so
    they get regenerated. Fail-open on verifier errors (question is kept).
    """
    if not questions:
        return [], []

    verdicts = await asyncio.gather(
        *(_verify_one(q, requested_difficulty) for q in questions)
    )

    kept: list[dict] = []
    rejected: list[dict] = []
    for q, verdict in zip(questions, verdicts):
        if verdict is None:  # verifier could not run -> fail open
            kept.append(q)
            continue
        reason = _rejection_reason(verdict)
        if reason is None:
            kept.append(q)
        else:
            logger.info("Verification rejected a question (%s)", reason)
            rejected.append(q)

    return kept, rejected
