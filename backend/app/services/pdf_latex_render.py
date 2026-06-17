"""LaTeX-safe rendering for solution-key PDF generation."""

from __future__ import annotations

import re
from typing import Any

from app.services.tex_sanitize import sanitize_tex_field

# Plain-text characters that must be escaped outside math mode.
_LATEX_PLAIN_ESCAPES = (
    ("\\", r"\textbackslash{}"),
    ("&", r"\&"),
    ("%", r"\%"),
    ("$", r"\$"),
    ("#", r"\#"),
    ("_", r"\_"),
    ("{", r"\{"),
    ("}", r"\}"),
    ("~", r"\textasciitilde{}"),
    ("^", r"\textasciicircum{}"),
)


def latex_escape_plain(text: str) -> str:
    """Escape characters that are special in LaTeX text mode."""
    out = text
    for char, repl in _LATEX_PLAIN_ESCAPES:
        out = out.replace(char, repl)
    return out


def _normalize_math_inner(inner: str) -> str:
    """Clean a math fragment before wrapping in \\(...\\) or \\[...\\]."""
    cleaned = inner.strip()
    cleaned = cleaned.replace("$$", "")
    cleaned = re.sub(r"(?<![\\])\$", "", cleaned)
    cleaned = re.sub(r"\\\\(?=[a-zA-Z{([\]|])", r"\\", cleaned)
    return cleaned


def _wrap_math(inner: str, display: bool) -> str:
    body = _normalize_math_inner(inner)
    if not body:
        return ""
    if display:
        return f"\\[{body}\\]"
    return f"\\({body}\\)"


def _prose_to_latex(text: str) -> str:
    """Convert prose (with real newlines) to LaTeX text-mode lines."""
    text = text.replace("\r\n", "\n")
    lines = text.split("\n")
    return "\\\\\n".join(latex_escape_plain(line) for line in lines)


def prepare_prose_for_pdf(text: str | None) -> str:
    """
    Normalize stored question/solution strings for PDF (no $ auto-wrapping).

    Fixes JSON corruption, literal ``\\n``, and ``\\newline`` markers.
    """
    if not text:
        return ""
    out = sanitize_tex_field(text)
    out = out.replace("\\newline", "\n")
    return out


def split_math_segments(text: str) -> list[tuple[str, str]]:
    """
    Split *text* into ('text'|'math'|'display', content) segments.

    Only well-formed ``$...$`` / ``$$...$$`` delimiters are treated as math.
    """
    segments: list[tuple[str, str]] = []
    i = 0
    n = len(text)

    while i < n:
        if text.startswith("$$", i):
            end = text.find("$$", i + 2)
            if end == -1:
                segments.append(("text", text[i:]))
                break
            segments.append(("display", text[i + 2 : end]))
            i = end + 2
            continue

        if text[i] == "$":
            end = text.find("$", i + 1)
            if end == -1:
                segments.append(("text", text[i:]))
                break
            segments.append(("math", text[i + 1 : end]))
            i = end + 1
            continue

        next_math = min(
            [pos for pos in (text.find("$", i), text.find("$$", i)) if pos != -1],
            default=-1,
        )
        if next_math == -1:
            segments.append(("text", text[i:]))
            break
        if next_math > i:
            segments.append(("text", text[i:next_math]))
        i = next_math

    return segments


def render_mixed_latex_for_pdf(text: str | None) -> str:
    """
    Render mixed prose + LaTeX for XeLaTeX.

    Uses ``\\(...\\)`` / ``\\[...\\]`` instead of ``$...$`` to avoid delimiter
    collisions, and never auto-wraps bare commands (which caused ``$$$`` bugs).
    """
    if not text:
        return ""

    prepared = prepare_prose_for_pdf(text)
    parts: list[str] = []

    for kind, content in split_math_segments(prepared):
        if kind == "display":
            parts.append(_wrap_math(content, display=True))
        elif kind == "math":
            parts.append(_wrap_math(content, display=False))
        elif content:
            parts.append(_prose_to_latex(content))

    return "".join(parts)


def latex_escape_metadata(value: Any) -> str:
    """Escape short metadata strings (attempt id, topic names, etc.)."""
    return latex_escape_plain("" if value is None else str(value))
