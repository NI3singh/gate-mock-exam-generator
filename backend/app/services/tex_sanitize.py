"""Normalize LaTeX-bearing text fields before persisting generated questions."""

from __future__ import annotations

import re

# LaTeX commands that start with \\n — keep literal \\n (do not convert to newline).
_LATEX_N_PREFIX = re.compile(
    r"^(?:eq|eg(?:medspace|thickspace|thinspace)?|ot|u|abla|ewline|ewcommand|"
    r"othing|mid|leftrightarrow|leftarrow|rightarrow|sim|subseteq|supseteq|"
    r"subset|supset|times|cong|dash|atural|parallel|prec|preceq|succeq|geq|"
    r"leq|gtr|exists|in|i|e|approx|uances|umber)"
)


def repair_json_escape_corruption(text: str) -> str:
    """Fix LaTeX broken by JSON \\t, \\r, \\f, \\b escape sequences."""
    if not text:
        return text
    replacements = (
        ("\t", "ext{", "\\text{"),
        ("\t", "exttt{", "\\texttt{"),
        ("\t", "extbf{", "\\textbf{"),
        ("\t", "extit{", "\\textit{"),
        ("\t", "imes", "\\times"),
        ("\t", "heta", "\\theta"),
        ("\t", "au", "\\tau"),
        ("\r", "ightarrow", "\\rightarrow"),
        ("\r", "angle", "\\rangle"),
        ("\f", "rac{", "\\frac{"),
        ("\f", "orall", "\\forall"),
        ("\b", "eta", "\\beta"),
    )
    out = text
    for ctrl, suffix, fixed in replacements:
        out = out.replace(ctrl + suffix, fixed)
    # Visible corruption when control chars were stripped
    out = re.sub(r"(?<![\\a-zA-Z{])ext\{", r"\\text{", out)
    out = re.sub(r"(?<![\\a-zA-Z])orall\b", r"\\forall", out)
    out = re.sub(r"(?<![\\a-zA-Z])ightarrow\b", r"\\rightarrow", out)
    out = re.sub(r"(?<![\\a-zA-Z])rac\{", r"\\frac{", out)
    return out


def _unescape_literal_newlines_outside_math(chunk: str) -> str:
    def repl(match: re.Match[str]) -> str:
        after = chunk[match.end() :]
        word = re.match(r"[a-zA-Z]+", after)
        if word and _LATEX_N_PREFIX.match(word.group(0)):
            return match.group(0)
        return "\n"

    return re.sub(r"\\n", repl, chunk)


def unescape_literal_newlines(text: str) -> str:
    """Turn literal \\n in solutions into real newlines (keep \\neq, \\neg, …)."""
    if not text:
        return text
    parts: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == "$":
            if i + 1 < n and text[i + 1] == "$":
                end = text.find("$$", i + 2)
                if end == -1:
                    parts.append(text[i:])
                    break
                parts.append(text[i : end + 2])
                i = end + 2
                continue
            end = text.find("$", i + 1)
            if end == -1:
                parts.append(text[i:])
                break
            parts.append(text[i : end + 1])
            i = end + 1
            continue
        next_dollar = text.find("$", i)
        chunk = text[i:] if next_dollar == -1 else text[i:next_dollar]
        parts.append(_unescape_literal_newlines_outside_math(chunk))
        i = n if next_dollar == -1 else next_dollar
    return "".join(parts)


def sanitize_tex_field(text: str | None) -> str:
    """Best-effort cleanup for stem_tex, solution_tex, and choice strings."""
    if not text:
        return text or ""
    out = repair_json_escape_corruption(text)
    out = unescape_literal_newlines(out)
    return out


def sanitize_question_fields(question: dict) -> dict:
    """Return a copy of *question* with normalized LaTeX text fields."""
    q = dict(question)
    for key in ("stem_tex", "solution_tex"):
        if key in q and isinstance(q[key], str):
            q[key] = sanitize_tex_field(q[key])
    choices = q.get("choices")
    if isinstance(choices, list):
        q["choices"] = [
            sanitize_tex_field(c) if isinstance(c, str) else c for c in choices
        ]
    return q
