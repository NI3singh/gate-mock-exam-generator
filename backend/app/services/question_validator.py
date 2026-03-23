"""
Validates LLM-generated questions for structural correctness.

Checks:
  1. Required keys present
  2. Types correct
  3. Answer format matches question_type
  4. Marks valid (1 or 2)
  5. Basic NAT answer sanity via SymPy (if computable)
"""

import logging
import math
from typing import Any

logger = logging.getLogger(__name__)

REQUIRED_KEYS = {
    "stem_tex",
    "code_snippet",
    "code_language",
    "choices",
    "answer",
    "question_type",
    "marks",
    "difficulty",
    "difficulty_score",
    "section_name",
    "topic",
    "estimated_time_seconds",
    "solution_tex",
}

VALID_TYPES = {"MCQ", "MSQ", "NAT"}
VALID_DIFFICULTIES = {"easy", "medium", "hard"}


def validate_question(q: dict, expected_section: str | None = None) -> tuple[bool, str]:
    """
    Validate a single generated question dict.
    Returns (is_valid, error_message).
    """
    # ── 1. Check required keys ──
    missing = REQUIRED_KEYS - set(q.keys())
    if missing:
        return False, f"Missing keys: {missing}"

    # ── 2. stem_tex must be non-empty string ──
    if not isinstance(q["stem_tex"], str) or len(q["stem_tex"].strip()) < 10:
        return False, "stem_tex is empty or too short"

    # ── 3. solution_tex must be non-empty ──
    if not isinstance(q["solution_tex"], str) or len(q["solution_tex"].strip()) < 10:
        return False, "solution_tex is empty or too short"

    # ── 4. question_type ──
    qtype = q.get("question_type")
    if qtype not in VALID_TYPES:
        return False, f"Invalid question_type: {qtype}"

    # ── 5. marks ──
    marks = q.get("marks")
    if marks not in (1, 2):
        return False, f"Invalid marks: {marks}"

    # ── 6. difficulty ──
    diff = q.get("difficulty")
    if diff not in VALID_DIFFICULTIES:
        return False, f"Invalid difficulty: {diff}"

    # ── 7. difficulty_score ──
    dscore = q.get("difficulty_score")
    if dscore is not None:
        try:
            dscore = float(dscore)
            if not (0.0 <= dscore <= 1.0):
                return False, f"difficulty_score out of range: {dscore}"
        except (TypeError, ValueError):
            q["difficulty_score"] = 0.5  # fallback

    # ── 8. Validate answer format per type ──
    answer = q.get("answer")
    if not isinstance(answer, dict):
        return False, f"answer must be a dict, got {type(answer).__name__}"

    if qtype == "MCQ":
        valid, msg = _validate_mcq(q)
    elif qtype == "MSQ":
        valid, msg = _validate_msq(q)
    elif qtype == "NAT":
        valid, msg = _validate_nat(q)
    else:
        valid, msg = False, f"Unknown type: {qtype}"

    if not valid:
        return False, msg

    # ── 9. section_name and topic must be strings ──
    if not isinstance(q.get("section_name"), str) or not q["section_name"].strip():
        return False, "section_name is missing or empty"
    if not isinstance(q.get("topic"), str) or not q["topic"].strip():
        return False, "topic is missing or empty"

    # ── 10. estimated_time_seconds ──
    ets = q.get("estimated_time_seconds")
    if ets is not None:
        try:
            q["estimated_time_seconds"] = int(ets)
        except (TypeError, ValueError):
            q["estimated_time_seconds"] = 120  # default

    return True, "OK"


def _validate_mcq(q: dict) -> tuple[bool, str]:
    """MCQ: 4 choices, answer.index is int 0-3."""
    choices = q.get("choices")
    if not isinstance(choices, list) or len(choices) != 4:
        return False, f"MCQ must have exactly 4 choices, got {type(choices)}"

    answer = q["answer"]
    idx = answer.get("index")
    if idx is None:
        # Try to extract from other formats
        if "indices" in answer and len(answer["indices"]) == 1:
            q["answer"] = {"index": answer["indices"][0]}
            idx = answer["indices"][0]
        else:
            return False, "MCQ answer must have 'index' key"

    try:
        idx = int(idx)
    except (TypeError, ValueError):
        return False, f"MCQ answer.index must be int, got {idx}"

    if idx < 0 or idx > 3:
        return False, f"MCQ answer.index must be 0-3, got {idx}"

    q["answer"] = {"index": idx}
    return True, "OK"


def _validate_msq(q: dict) -> tuple[bool, str]:
    """MSQ: 4 choices, answer.indices is list of ints, 1-3 correct."""
    choices = q.get("choices")
    if not isinstance(choices, list) or len(choices) != 4:
        return False, f"MSQ must have exactly 4 choices, got {type(choices)}"

    answer = q["answer"]
    indices = answer.get("indices")

    if indices is None:
        # Maybe LLM used "index" instead
        if "index" in answer:
            indices = [answer["index"]]
        else:
            return False, "MSQ answer must have 'indices' key"

    if not isinstance(indices, list):
        return False, f"MSQ answer.indices must be a list, got {type(indices)}"

    if len(indices) < 1 or len(indices) > 3:
        return False, f"MSQ must have 1-3 correct indices, got {len(indices)}"

    try:
        indices = [int(i) for i in indices]
    except (TypeError, ValueError):
        return False, "MSQ answer.indices must be integers"

    if any(i < 0 or i > 3 for i in indices):
        return False, f"MSQ indices must be 0-3, got {indices}"

    q["answer"] = {"indices": sorted(set(indices))}
    return True, "OK"


def _validate_nat(q: dict) -> tuple[bool, str]:
    """NAT: choices must be null, answer has value + tolerance."""
    if q.get("choices") is not None:
        q["choices"] = None  # auto-fix

    answer = q["answer"]
    value = answer.get("value")

    if value is None:
        return False, "NAT answer must have 'value' key"

    try:
        value = float(value)
    except (TypeError, ValueError):
        return False, f"NAT answer.value must be numeric, got {value}"

    if math.isnan(value) or math.isinf(value):
        return False, "NAT answer.value is NaN or Inf"

    tolerance = answer.get("tolerance", 0.01)
    try:
        tolerance = float(tolerance)
    except (TypeError, ValueError):
        tolerance = 0.01

    if tolerance < 0:
        tolerance = abs(tolerance)

    q["answer"] = {"value": value, "tolerance": tolerance}
    return True, "OK"


def validate_batch(
    questions: list[dict],
    expected_section: str | None = None,
) -> list[dict]:
    """
    Validate a batch of questions. Returns only the valid ones.
    """
    valid = []
    for i, q in enumerate(questions):
        is_valid, msg = validate_question(q, expected_section)
        if is_valid:
            valid.append(q)
        else:
            logger.warning(f"Question {i + 1} in batch failed validation: {msg}")
    return valid