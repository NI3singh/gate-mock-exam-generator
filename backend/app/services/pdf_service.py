from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from uuid import UUID

import httpx
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.schemas.attempt import AttemptDetailResponse
from app.services.attempt_detail_service import build_attempt_detail
from app.services.pdf_latex_render import latex_escape_metadata, render_mixed_latex_for_pdf

BACKEND_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
GENERATED_PDFS_DIR = BACKEND_ROOT / "generated_pdfs"

LATEX_TIMEOUT = httpx.Timeout(120.0, connect=20.0, read=120.0, write=20.0)

_JINJA = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True,
)


def _latex_text(value: Any) -> str:
    return latex_escape_metadata(value)


_JINJA.filters["latex_text"] = _latex_text


def _render_mixed_latex(text: str | None) -> str:
    return render_mixed_latex_for_pdf(text)


def _choice_label(index: int) -> str:
    return chr(65 + index)


def _correct_choice_indices(solution: dict[str, Any]) -> set[int]:
    correct_answer = solution.get("correct_answer") or {}
    question_type = solution.get("question_type")

    if question_type == "MCQ":
        index = correct_answer.get("index")
        return {index} if isinstance(index, int) else set()

    if question_type == "MSQ":
        return {
            index
            for index in correct_answer.get("indices", [])
            if isinstance(index, int)
        }

    return set()


def _format_correct_answer_tex(solution: dict[str, Any]) -> str:
    correct_answer = solution.get("correct_answer") or {}
    question_type = solution.get("question_type")

    if question_type == "MCQ":
        index = correct_answer.get("index")
        return f"Option {_choice_label(index)}" if isinstance(index, int) else "N/A"

    if question_type == "MSQ":
        indices = [
            _choice_label(index)
            for index in correct_answer.get("indices", [])
            if isinstance(index, int)
        ]
        return f"Options {', '.join(indices)}" if indices else "N/A"

    value = latex_escape_metadata(correct_answer.get("value", ""))
    tolerance = correct_answer.get("tolerance")
    if tolerance is None:
        return value or "N/A"

    return f"{value} (tolerance \\(\\pm {latex_escape_metadata(tolerance)}\\))"


def _listings_language(language: str | None) -> str:
    normalized = (language or "").strip().lower()
    if normalized == "python":
        return "Python"
    if normalized in {"c", "cpp", "c++"}:
        return "C"
    return ""


def _serialize_attempt_detail(detail: AttemptDetailResponse) -> dict[str, Any]:
    if hasattr(detail, "model_dump"):
        return detail.model_dump()
    return detail.dict()


def _build_template_context(detail: AttemptDetailResponse) -> dict[str, Any]:
    payload = _serialize_attempt_detail(detail)

    solutions: list[dict[str, Any]] = []
    for solution in payload.get("solutions", []):
        correct_indices = _correct_choice_indices(solution)
        choices = []
        for index, choice in enumerate(solution.get("choices") or []):
            choices.append(
                {
                    "label": _choice_label(index),
                    "content_tex": _render_mixed_latex(choice),
                    "is_correct": index in correct_indices,
                }
            )

        solutions.append(
            {
                "qno": solution["qno"],
                "question_type": solution["question_type"],
                "marks": solution["marks"],
                "section_name": solution["section_name"],
                "topic": solution["topic"],
                "stem_tex": _render_mixed_latex(solution.get("stem_tex")),
                "code_snippet": solution.get("code_snippet") or "",
                "listings_language": _listings_language(solution.get("code_language")),
                "choices": choices,
                "correct_answer_tex": _format_correct_answer_tex(solution),
                "solution_tex": _render_mixed_latex(solution.get("solution_tex")),
            }
        )

    return {
        "attempt_id": payload["attempt_id"],
        "exam_id": payload["exam_id"],
        "paper": payload["paper"],
        "difficulty": payload["difficulty"],
        "score": payload["score"],
        "max_score": payload["max_score"],
        "total_questions": payload["total_questions"],
        "total_marks": payload["total_marks"],
        "duration_minutes": payload["duration_minutes"],
        "total_correct": payload["total_correct"],
        "total_wrong": payload["total_wrong"],
        "total_unanswered": payload["total_unanswered"],
        "solutions": solutions,
    }


def render_solution_key_tex(detail: AttemptDetailResponse) -> str:
    template = _JINJA.get_template("solutions_key.tex.j2")
    return template.render(**_build_template_context(detail))


def _extract_compile_error(response: httpx.Response) -> str:
    if not response.content:
        return "No response body returned from LaTeX compiler."

    content_type = response.headers.get("content-type", "").lower()
    if "application/json" in content_type:
        try:
            payload = response.json()
        except json.JSONDecodeError:
            return response.text[:2000]

        if isinstance(payload, dict):
            for key in ("detail", "message", "error"):
                value = payload.get(key)
                if value:
                    if str(value) != "COMPILATION_ERROR":
                        return str(value)[:2000]

            for key in ("logs", "output", "log", "stderr"):
                value = payload.get(key)
                if value:
                    return str(value)[:2000]

            log_files = payload.get("log_files")
            if isinstance(log_files, dict):
                combined_logs = "\n".join(str(content) for content in log_files.values())
                interesting_lines = [
                    line.strip()
                    for line in combined_logs.splitlines()
                    if (
                        "LaTeX Error" in line
                        or "Unicode character" in line
                        or line.startswith("!")
                        or "Fatal error" in line
                    )
                ]
                if interesting_lines:
                    return " | ".join(interesting_lines[:5])[:2000]

        return json.dumps(payload)[:2000]

    return response.text[:2000]


async def _compile_latex_to_pdf(tex_content: str) -> bytes:
    expected_sections = tex_content.count(r"\section*{Question")
    payload = {
        "compiler": settings.LATEX_COMPILER,
        "resources": [
            {
                "main": True,
                "content": tex_content,
            }
        ],
        "options": {
            "compiler": {
                "halt_on_error": True,
                "silent": False,
            },
            "response": {
                "log_files_on_failure": True,
            },
        },
    }

    async with httpx.AsyncClient(timeout=LATEX_TIMEOUT) as client:
        response = await client.post(settings.LATEX_BUILD_URL, json=payload)

    content_type = response.headers.get("content-type", "").lower()

    if response.status_code >= 400:
        raise RuntimeError(
            f"LaTeX.online request failed with status {response.status_code}: "
            f"{_extract_compile_error(response)}"
        )

    if not response.content.startswith(b"%PDF"):
        raise RuntimeError(
            "LaTeX compilation did not return a PDF: "
            f"{_extract_compile_error(response)}"
        )

    # Reject truncated PDFs when the compiler reports failure in JSON metadata.
    if "application/json" in content_type:
        try:
            meta = response.json()
            status = str(meta.get("status", "")).lower()
            if status in {"error", "failed", "failure"}:
                raise RuntimeError(
                    "LaTeX compilation failed: "
                    f"{_extract_compile_error(response)}"
                )
        except json.JSONDecodeError:
            pass

    if expected_sections >= 10 and len(response.content) < 50_000:
        raise RuntimeError(
            f"LaTeX PDF looks truncated ({len(response.content)} bytes for "
            f"{expected_sections} questions). Check the LaTeX log."
        )

    return response.content


def _pdf_path_for_attempt(attempt_id: str) -> Path:
    GENERATED_PDFS_DIR.mkdir(parents=True, exist_ok=True)
    return GENERATED_PDFS_DIR / f"solutions_{attempt_id}.pdf"


def _pdf_meta_path(pdf_path: Path) -> Path:
    return pdf_path.with_suffix(".meta")


async def generate_solutions_pdf(
    db: AsyncSession,
    attempt_id: str,
    user_id: UUID | str,
    *,
    force_regenerate: bool = False,
) -> Path:
    detail = await build_attempt_detail(db, attempt_id, user_id)
    solution_count = len(detail.solutions)

    pdf_path = _pdf_path_for_attempt(attempt_id)
    meta_path = _pdf_meta_path(pdf_path)

    cached_count: int | None = None
    if meta_path.exists():
        try:
            cached_count = int(meta_path.read_text(encoding="utf-8").strip())
        except ValueError:
            cached_count = None

    if (
        not force_regenerate
        and pdf_path.exists()
        and pdf_path.stat().st_size > 0
        and cached_count == solution_count
        and solution_count >= detail.total_questions
        and pdf_path.stat().st_size >= max(50_000, solution_count * 800)
    ):
        return pdf_path

    tex_content = render_solution_key_tex(detail)
    pdf_bytes = await _compile_latex_to_pdf(tex_content)
    pdf_path.write_bytes(pdf_bytes)
    meta_path.write_text(str(solution_count), encoding="utf-8")
    return pdf_path
