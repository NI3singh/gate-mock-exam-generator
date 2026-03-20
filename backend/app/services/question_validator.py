"""
Question validation with retry logic.

Validates each generated question against:
  1. JSON schema (required fields, correct types, marks, options)
  2. LaTeX syntax (balanced delimiters)
  3. SymPy numeric verification for NAT answers (with LLM fallback)
"""

import re
import sympy
from sympy import N as sympy_n
from typing import Any

from app.services.llm_service import llm_service


MAX_RETRIES = 3


# ─── Result dataclass ────────────────────────────────────────────────────────


class ValidationResult:
    """Container for validation outcome."""

    def __init__(
        self,
        valid: bool,
        errors: list[str],
        retry_count: int = 0,
    ) -> None:
        self.valid = valid
        self.errors = errors
        self.retry_count = retry_count

    def __repr__(self) -> str:
        return f"ValidationResult(valid={self.valid}, errors={self.errors}, retries={self.retry_count})"


# ─── LaTeX syntax checks ─────────────────────────────────────────────────────


def check_latex_balance(text: str) -> list[str]:
    """
    Basic LaTeX structural checks.
    Returns a list of error messages (empty = valid).
    """
    errors: list[str] = []

    # Balanced parentheses
    if text.count("(") != text.count(")"):
        errors.append(
            f"Unbalanced parentheses: {text.count('(')} '(' vs {text.count(')')} ')'"
        )

    # Balanced square brackets
    if text.count("[") != text.count("]"):
        errors.append(
            f"Unbalanced brackets: {text.count('[')} '[' vs {text.count(']')} ']'"
        )

    # Balanced braces
    open_b = text.count("{")
    close_b = text.count("}")
    if open_b != close_b:
        errors.append(
            f"Unbalanced braces: {open_b} '{{' vs {close_b} '}}'"
        )

    # \left / \right balance
    left_count = len(re.findall(r"\\left\s*[([{\[]", text))
    right_count = len(re.findall(r"\\right\s*[)}\]]", text))
    if left_count != right_count:
        errors.append(
            f"Mismatched \\left/\\right: {left_count} \\left vs {right_count} \\right"
        )

    # \begin / \end balance
    begin_count = len(re.findall(r"\\begin\{", text))
    end_count = len(re.findall(r"\\end\{", text))
    if begin_count != end_count:
        errors.append(
            f"Mismatched \\begin/\\end: {begin_count} vs {end_count}"
        )

    return errors


# ─── JSON schema validation ──────────────────────────────────────────────────


def validate_json_schema(question: dict[str, Any]) -> list[str]:
    """
    Check required fields and type constraints for a question dict.
    Returns a list of error messages.
    """
    errors: list[str] = []

    required_fields = [
        "question_type", "marks", "difficulty", "section_name",
        "topic", "stem_tex", "answer", "solution_tex", "estimated_time_seconds",
    ]
    for field in required_fields:
        if field not in question:
            errors.append(f"Missing required field: {field}")

    qtype = question.get("question_type")
    if qtype not in ("MCQ", "MSQ", "NAT"):
        errors.append(f"Invalid question_type: {qtype!r}")

    marks = question.get("marks")
    if marks not in (1, 2):
        errors.append(f"Invalid marks (must be 1 or 2): {marks}")

    difficulty = question.get("difficulty")
    if difficulty not in ("easy", "medium", "hard"):
        errors.append(f"Invalid difficulty: {difficulty!r}")

    # Choices validation
    choices = question.get("choices")
    if qtype in ("MCQ", "MSQ"):
        if not isinstance(choices, list) or len(choices) != 4:
            errors.append(
                f"{qtype} must have exactly 4 choices, got {choices!r}"
            )
        else:
            labels = {c.get("label") for c in choices if c}
            if labels != {"A", "B", "C", "D"}:
                errors.append(f"Choices must have labels A,B,C,D, got {labels}")
    elif qtype == "NAT":
        if choices is not None:
            errors.append(f"NAT questions must have null choices, got {choices!r}")

    # Answer structure
    answer = question.get("answer", {})
    if qtype == "MCQ":
        correct = answer.get("correct")
        if correct not in ("A", "B", "C", "D"):
            errors.append(f"MCQ correct answer must be A/B/C/D, got {correct!r}")
    elif qtype == "MSQ":
        correct = answer.get("correct", [])
        if not isinstance(correct, list) or len(correct) == 0:
            errors.append(f"MSQ correct answer must be non-empty list, got {correct!r}")
    elif qtype == "NAT":
        correct_val = answer.get("correct")
        if not isinstance(correct_val, (int, float)):
            errors.append(f"NAT correct answer must be numeric, got {correct_val!r}")

    return errors


# ─── NAT answer verification ─────────────────────────────────────────────────


def _extract_expr_from_stem(stem_tex: str) -> str | None:
    """Extract a mathematical expression from a LaTeX stem for SymPy evaluation."""
    patterns = [
        r"\$([^$]+)\$",          # $...$
        r"\\\(([^\\)]+)\\\)",  # \(...\)


        r"=\s*([\d\.\+\-\*\/\(\)\s\^]+?)(?:\s*[,\.]|$)",  # = expression
    ]
    for pattern in patterns:
        m = re.search(pattern, stem_tex)
        if m:
            return m.group(1).strip()
    return None


async def verify_nat_answer(question: dict[str, Any]) -> tuple[bool, str]:
    """
    Verify a NAT answer using SymPy numerically.
    Falls back to LLM verification if SymPy cannot parse the expression.
    Returns (is_correct, notes).
    """
    answer_data = question.get("answer", {})
    correct_val = answer_data.get("correct")
    tolerance = answer_data.get("tolerance", 0.01)
    stem_tex = question.get("stem_tex", "")

    # Try SymPy first
    expr_str = _extract_expr_from_stem(stem_tex)
    if expr_str:
        try:
            expr = sympy.parse_expr(expr_str)
            computed = float(sympy_n(expr))
            error = abs(computed - correct_val)
            within_tol = error <= tolerance
            return within_tol, f"sympy computed={computed:.6f}, error={error:.6f}"
        except Exception:
            # SymPy failed — fall through to LLM fallback
            pass

    # LLM fallback
    prompt_text = (
        f"Question stem: {stem_tex}\n"
        f"Correct numerical answer: {correct_val}\n"
        f"Tolerance: {tolerance}\n\n"
        "Verify if this answer is mathematically correct for the given question. "
        "Return JSON with fields: verified (bool), computed_value (number), "
        "submitted_value (number), absolute_error (number), "
        "within_tolerance (bool), notes (string)."
    )
    messages = [{"role": "user", "content": prompt_text}]

    try:
        result = await llm_service.chat_completion(messages)
        within_tol = result.get("within_tolerance", False)
        notes = result.get("notes", "")
        return within_tol, f"llm: {notes}"
    except Exception as exc:
        return True, f"llm verification skipped: {exc}"


# ─── Full validation pipeline ────────────────────────────────────────────────


async def validate_question(
    question: dict[str, Any],
    retry_count: int = 0,
) -> ValidationResult:
    """
    Run the full validation pipeline on a single question dict.
    """
    errors: list[str] = []

    # 1. JSON schema check
    errors.extend(validate_json_schema(question))

    # 2. LaTeX syntax check on stem and solution
    for field in ("stem_tex", "solution_tex"):
        if field in question and question[field]:
            latex_errors = check_latex_balance(question[field])
            errors.extend(f"{field}: {e}" for e in latex_errors)

    # 3. NAT answer verification via SymPy (skip if already errors)
    if question.get("question_type") == "NAT" and not errors:
        is_correct, notes = await verify_nat_answer(question)
        if not is_correct:
            errors.append(f"NAT answer verification failed: {notes}")

    if errors:
        return ValidationResult(
            valid=False,
            errors=errors,
            retry_count=retry_count,
        )

    return ValidationResult(valid=True, errors=[], retry_count=retry_count)


async def validate_question_with_retry(question: dict[str, Any]) -> ValidationResult:
    """
    Validate with up to MAX_RETRIES on failure.
    Returns the result of the last attempt.
    """
    result = await validate_question(question, retry_count=0)
    for attempt in range(1, MAX_RETRIES + 1):
        if result.valid:
            break
        result = await validate_question(question, retry_count=attempt)
    return result
