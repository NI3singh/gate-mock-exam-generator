"""
Render LaTeX-bearing question / solution text into clean, compile-safe LaTeX
for the solution-key PDF.

This mirrors the frontend ``mathRender.ts`` pipeline so the downloaded PDF
matches what students see on screen:

    repair JSON-escape corruption
    -> normalise over-escaped backslashes
    -> turn literal "\\n" into real newlines
    -> normalise \\( \\) \\[ \\] delimiters into $ / $$
    -> auto-wrap bare LaTeX commands (e.g. ``\\forall x``) in $...$

It then emits **compile-safe** LaTeX, which is what stops the old PDF from
getting silently truncated by the LaTeX engine:

    * unbalanced ``$`` / ``$$`` never start runaway math (treated as literal)
    * line breaks become paragraphs (no fragile / illegal ``\\``)
    * display math is wrapped so an inner ``\\`` or ``&`` cannot break it
    * common Unicode math symbols are mapped to LaTeX commands
    * ``%`` and ``#`` inside math are protected so they cannot eat content

Only the rendering of free-text fields lives here.  Simple scalar fields
(topic, section, NAT answers) keep using ``pdf_service._latex_text``.
"""

from __future__ import annotations

import re

from app.services.tex_sanitize import (
    repair_json_escape_corruption,
    unescape_literal_newlines,
)

# ── character helpers ────────────────────────────────────────────────────────

# Mirror of the frontend MATH_SYMBOL class: [+\-*/=<>^_|().,:;!'~[\]?]
_MATH_SYMBOL = set("+-*/=<>^_|().,:;!'~[]?")


def _is_letter(c: str) -> bool:
    return ("A" <= c <= "Z") or ("a" <= c <= "z")


def _is_digit(c: str) -> bool:
    return "0" <= c <= "9"


# ── LaTeX text escaping ──────────────────────────────────────────────────────

_LATEX_SPECIALS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def _escape_text(s: str) -> str:
    """Escape LaTeX special characters in plain (non-math) text."""
    return "".join(_LATEX_SPECIALS.get(ch, ch) for ch in s)


# ── Unicode normalisation ────────────────────────────────────────────────────
# Math symbols: used raw inside math mode, wrapped in $...$ inside text.
_UNICODE_MATH: dict[str, str] = {
    "×": r"\times", "÷": r"\div", "±": r"\pm", "∓": r"\mp", "−": "-",
    "·": r"\cdot", "⋅": r"\cdot", "∗": "*", "∙": r"\bullet",
    "≤": r"\leq", "≥": r"\geq", "≠": r"\neq", "≈": r"\approx", "≅": r"\cong",
    "≡": r"\equiv", "∼": r"\sim", "∝": r"\propto", "≪": r"\ll", "≫": r"\gg",
    "→": r"\rightarrow", "←": r"\leftarrow", "↔": r"\leftrightarrow",
    "⇒": r"\Rightarrow", "⇐": r"\Leftarrow", "⇔": r"\Leftrightarrow",
    "↦": r"\mapsto", "⟶": r"\longrightarrow", "⟹": r"\Longrightarrow",
    "∀": r"\forall", "∃": r"\exists", "∄": r"\nexists", "∈": r"\in",
    "∉": r"\notin", "∋": r"\ni", "∅": r"\emptyset", "∖": r"\setminus",
    "⊆": r"\subseteq", "⊂": r"\subset", "⊇": r"\supseteq", "⊃": r"\supset",
    "∪": r"\cup", "∩": r"\cap", "∧": r"\wedge", "∨": r"\vee", "¬": r"\neg",
    "⊕": r"\oplus", "⊗": r"\otimes", "⊤": r"\top", "⊥": r"\bot",
    "∞": r"\infty", "∂": r"\partial", "∇": r"\nabla", "∑": r"\sum",
    "∏": r"\prod", "∫": r"\int", "√": r"\surd", "∠": r"\angle",
    "∴": r"\therefore", "∵": r"\because", "∘": r"\circ",
    "⌈": r"\lceil", "⌉": r"\rceil", "⌊": r"\lfloor", "⌋": r"\rfloor",
    "⟨": r"\langle", "⟩": r"\rangle", "…": r"\ldots", "⋯": r"\cdots",
    "′": "'", "″": "''", "°": r"{}^{\circ}",
    "✓": r"\checkmark", "✗": r"\times", "✘": r"\times", "∎": r"\blacksquare",
    "ℝ": r"\mathbb{R}", "ℕ": r"\mathbb{N}", "ℤ": r"\mathbb{Z}",
    "ℚ": r"\mathbb{Q}", "ℂ": r"\mathbb{C}",
    # Greek (lower)
    "α": r"\alpha", "β": r"\beta", "γ": r"\gamma", "δ": r"\delta",
    "ε": r"\varepsilon", "ϵ": r"\epsilon", "ζ": r"\zeta", "η": r"\eta",
    "θ": r"\theta", "ϑ": r"\vartheta", "ι": r"\iota", "κ": r"\kappa",
    "λ": r"\lambda", "μ": r"\mu", "ν": r"\nu", "ξ": r"\xi", "π": r"\pi",
    "ρ": r"\rho", "σ": r"\sigma", "ς": r"\varsigma", "τ": r"\tau",
    "υ": r"\upsilon", "φ": r"\varphi", "ϕ": r"\phi", "χ": r"\chi",
    "ψ": r"\psi", "ω": r"\omega",
    # Greek (upper)
    "Γ": r"\Gamma", "Δ": r"\Delta", "Θ": r"\Theta", "Λ": r"\Lambda",
    "Ξ": r"\Xi", "Π": r"\Pi", "Σ": r"\Sigma", "Φ": r"\Phi", "Ψ": r"\Psi",
    "Ω": r"\Omega",
}

# Punctuation handled only in text mode (applied before the math map).
_UNICODE_TEXT_ONLY: dict[str, str] = {
    "\u00A0": '~',  # no-break space
    "\u202F": '~',  # narrow no-break space
    "\u2009": '\\,',  # thin space
    "\u2018": '`',  # left single quote
    "\u2019": "'",  # right single quote / apostrophe
    "\u201C": '``',  # left double quote
    "\u201D": "''",  # right double quote
    "\u2013": '--',  # en dash
    "\u2014": '---',  # em dash
    "\u2212": '-',  # minus sign
    "\u2026": '\\ldots{}',  # horizontal ellipsis
    "\u2022": '\\textbullet{}',  # bullet
    "\u20b9": 'Rs.~',  # indian rupee sign
}

_UNICODE_MATH_RE = re.compile("[" + re.escape("".join(_UNICODE_MATH.keys())) + "]")


def _apply_unicode_text(s: str) -> str:
    for k, v in _UNICODE_TEXT_ONLY.items():
        if k in s:
            s = s.replace(k, v)
    return _UNICODE_MATH_RE.sub(lambda m: "$" + _UNICODE_MATH[m.group(0)] + "$", s)


def _apply_unicode_math(s: str) -> str:
    return _UNICODE_MATH_RE.sub(lambda m: _UNICODE_MATH[m.group(0)], s)


# ── prepare pipeline (ported from frontend mathRender.ts) ────────────────────

_OVER_ESCAPED_HINT = re.compile(
    r"\\\\(?:forall|text|frac|cup|cap|neg|rightarrow|leftarrow|times|qquad|leq|geq)"
)

# Extra JSON-escape repairs present in the frontend but not in tex_sanitize.
_TAB, _CR, _FF, _BS = "\t", "\r", "\f", "\b"
_SUPPLEMENTAL_REPAIRS: tuple[tuple[str, str], ...] = (
    (_TAB + "extsc{", r"\textsc{"),
    (_TAB + "extrm{", r"\textrm{"),
    (_TAB + "riangle", r"\triangle"),
    (_CR + "ceil", r"\rceil"),
    (_CR + "floor", r"\rfloor"),
    (_BS + "inom{", r"\binom{"),
    (_BS + "igg", r"\bigg"),
    (_BS + "ig", r"\big"),
)


def _supplement_repair(text: str) -> str:
    for corrupt, fixed in _SUPPLEMENTAL_REPAIRS:
        if corrupt in text:
            text = text.replace(corrupt, fixed)
    return text


def _outside_math(text: str, fn) -> str:
    """Apply ``fn`` only to spans of *text* that are outside $...$ / $$...$$."""
    out: list[str] = []
    i, n = 0, len(text)
    while i < n:
        if text[i] == "$":
            if i + 1 < n and text[i + 1] == "$":
                end = text.find("$$", i + 2)
                if end == -1:
                    out.append(text[i:])
                    break
                out.append(text[i : end + 2])
                i = end + 2
                continue
            end = text.find("$", i + 1)
            if end == -1:
                out.append(text[i:])
                break
            out.append(text[i : end + 1])
            i = end + 1
            continue
        nxt = text.find("$", i)
        chunk = text[i:] if nxt == -1 else text[i:nxt]
        out.append(fn(chunk))
        i = n if nxt == -1 else nxt
    return "".join(out)


def _normalize_over_escaped(text: str) -> str:
    if "\\\\" not in text:
        return text

    def _norm(chunk: str) -> str:
        if "\\\\" not in chunk or not _OVER_ESCAPED_HINT.search(chunk):
            return chunk
        return re.sub(r"\\\\(?=[a-zA-Z{(\[\]|;])", r"\\", chunk)

    return _outside_math(text, _norm)


def _expand_long_paragraph_breaks(text: str) -> str:
    if "\n" in text or len(text) < 350:
        return text
    return re.sub(r"\.\s+(?=[A-Z])", ".\n\n", text)


def _normalize_delimiters(text: str) -> str:
    text = re.sub(r"(?<!\\)\\\[", "$$", text)
    text = re.sub(r"(?<!\\)\\\]", "$$", text)
    text = re.sub(r"(?<!\\)\\\(", "$", text)
    text = re.sub(r"(?<!\\)\\\)", "$", text)
    return text


def _skip_balanced(text: str, pos: int, open_c: str, close_c: str) -> int:
    n = len(text)
    depth = 0
    while pos < n:
        c = text[pos]
        if c == "\\":
            pos += 2
            continue
        if c == open_c:
            depth += 1
        elif c == close_c:
            depth -= 1
            if depth == 0:
                return pos + 1
        pos += 1
    return n


def _find_run_end(text: str, start: int) -> int:
    """Maximal end (exclusive) of a bare-LaTeX run beginning at a backslash."""
    n = len(text)
    pos = start
    last_solid = start
    while pos < n:
        c = text[pos]
        if c == "$" or c == "\n":
            break

        if c == "\\":
            if pos + 1 < n:
                nx = text[pos + 1]
                if _is_letter(nx):
                    pos += 1
                    while pos < n and _is_letter(text[pos]):
                        pos += 1
                    if pos < n and text[pos] == "*":
                        pos += 1
                    while pos < n:
                        look = pos
                        while look < n and text[look] == " ":
                            look += 1
                        if look < n and (text[look] == "{" or text[look] == "["):
                            open_c = text[look]
                            close_c = "}" if open_c == "{" else "]"
                            pos = _skip_balanced(text, look, open_c, close_c)
                        else:
                            break
                    last_solid = pos
                    continue
                pos += 2
                last_solid = pos
                continue
            pos += 1
            last_solid = pos
            continue

        if c == "{":
            pos = _skip_balanced(text, pos, "{", "}")
            last_solid = pos
            continue

        if c == " " or c == "\t":
            look = pos
            while look < n and (text[look] == " " or text[look] == "\t"):
                look += 1
            if look >= n:
                break
            after = text[look]
            if after == "\n":
                break
            if after == "\\" or after == "{" or (after in _MATH_SYMBOL) or _is_digit(after):
                pos = look
                continue
            if _is_letter(after) and (look + 1 >= n or not _is_letter(text[look + 1])):
                pos = look
                continue
            break

        if (c in _MATH_SYMBOL) or _is_digit(c):
            pos += 1
            last_solid = pos
            continue

        if _is_letter(c):
            w = pos
            while w < n and _is_letter(text[w]):
                w += 1
            if w - pos == 1:
                pos = w
                last_solid = pos
                continue
            break

        break
    return last_solid


def _merge_adjacent_runs(text: str, runs: list[list[int]]) -> list[list[int]]:
    if not runs:
        return runs
    merged: list[list[int]] = [list(runs[0])]
    for s, e in runs[1:]:
        prev = merged[-1]
        gap = text[prev[1] : s]
        if len(gap) < 40 and re.fullmatch(r"[\s;]*(?:\(\d+\)[\s;]*)*", gap):
            prev[1] = e
        else:
            merged.append([s, e])
    return merged


def _collect_bare_latex_runs(text: str) -> list[list[int]]:
    n = len(text)
    runs: list[list[int]] = []
    i = 0
    while i < n:
        if text[i] == "$":
            if i + 1 < n and text[i + 1] == "$":
                end = text.find("$$", i + 2)
                i = n if end == -1 else end + 2
            else:
                end = text.find("$", i + 1)
                i = n if end == -1 else end + 1
            continue
        if text[i] == "\\" and i + 1 < n and _is_letter(text[i + 1]):
            e = _find_run_end(text, i)
            if e <= i:  # defensive: always make progress
                e = i + 1
            runs.append([i, e])
            i = e
            continue
        i += 1
    return _merge_adjacent_runs(text, runs)


def _wrap_bare_latex_runs(text: str) -> str:
    """Wrap bare ``\\command`` runs (outside existing math) in $...$ / $$...$$."""
    runs = _collect_bare_latex_runs(text)
    if not runs:
        return text
    out: list[str] = []
    cursor = 0
    for start, end in runs:
        abs_start, abs_end = start, end
        # Absorb a directly-adjacent vertical bar so |x| style stays together.
        if abs_start > cursor and text[abs_start - 1] == "|":
            abs_start -= 1
        if abs_end < len(text) and text[abs_end] == "|":
            abs_end += 1
        out.append(text[cursor:abs_start])
        slice_ = text[abs_start:abs_end]
        use_display = len(slice_) > 80 or bool(re.search(r"\\qquad|\\begin\{", slice_))
        delim = "$$" if use_display else "$"
        out.append(delim + slice_ + delim)
        cursor = abs_end
    out.append(text[cursor:])
    return "".join(out)


_TABLE_MARKERS = ("\\begin{tabular}", "\\hline", "\\multicolumn", "\\cline")


def _detable(text: str) -> str:
    """Flatten a (typically mangled) table into readable plain-text rows.

    Models emit data tables with ``\\begin{tabular}`` wrapped in ``$$``/``\\[`` and
    rows split across math blocks, escaped ``&``/``\\\\`` — i.e. a table inside
    math mode, which aborts compilation.  These are unrecoverable as real tables,
    so we drop the table scaffolding and keep the cell values as text rows.  This
    guarantees the question (and every question after it) still renders.
    """
    if not any(m in text for m in _TABLE_MARKERS):
        return text
    t = re.sub(r"(?<!\\)\$\$|(?<!\\)\$", " ", text)        # strip math delimiters
    t = re.sub(r"\\begin\{tabular\}\s*\{[^}]*\}", "", t)
    t = t.replace("\\end{tabular}", "")
    t = re.sub(
        r"\\begin\{(aligned|array|cases|split|smallmatrix|subarray|gathered"
        r"|[bBpvVn]?matrix)\}(\s*\[[^\]]*\])?(\s*\{[^}]*\})?",
        "",
        t,
    )
    t = re.sub(
        r"\\end\{(aligned|array|cases|split|smallmatrix|subarray|gathered"
        r"|[bBpvVn]?matrix)\}",
        "",
        t,
    )
    t = re.sub(r"\\hline|\\cline\{[^}]*\}", "", t)
    t = re.sub(r"\\multicolumn\{[^}]*\}\{[^}]*\}", "", t)
    t = re.sub(r"\\newline", "\n\n", t)
    t = t.replace("\\\\", "\n\n")                          # row breaks
    t = t.replace("&", "   ")                              # column separators
    return t


def _prepare(text: str) -> str:
    text = repair_json_escape_corruption(text)
    text = _supplement_repair(text)
    text = _normalize_over_escaped(text)
    text = unescape_literal_newlines(text)
    text = _detable(text)
    text = _expand_long_paragraph_breaks(text)
    text = _normalize_delimiters(text)
    text = _wrap_bare_latex_runs(text)
    return text


# ── compile-safe LaTeX emission ──────────────────────────────────────────────

_DISPLAY_ENVS = {
    "align", "gather", "equation", "multline", "flalign", "alignat",
    "eqnarray", "displaymath",
}
_SUB_MATH_ENV_RE = re.compile(
    r"\\begin\{(aligned|gathered|cases|split|array|smallmatrix|subarray"
    r"|[bBpvVn]?matrix)\}"
)


def _fix_over_escaped(s: str) -> str:
    if "\\\\" not in s or not _OVER_ESCAPED_HINT.search(s):
        return s
    return re.sub(r"\\\\(?=[a-zA-Z{(\[\]|;])", r"\\", s)


def _protect_math(c: str) -> str:
    """Neutralise characters that would let math silently swallow content."""
    c = re.sub(r"(?<!\\)%", r"\\%", c)   # a stray % comments out the rest of a line
    c = re.sub(r"(?<!\\)#", r"\\#", c)   # a raw # is a fatal "macro parameter" error
    return c


def _strip_math_dollars(c: str) -> str:
    """An unescaped '$' inside math content is always illegal -> drop it.

    Guarantees every '$' we emit comes from a real inline pair, so math mode
    can never bleed across questions (a cause of the downstream truncation).
    """
    return re.sub(r"(?<!\\)\$", "", c)


def _balance_braces(c: str) -> str:
    """Close unclosed groups and escape stray closers.

    A missing '}' (e.g. the model wrote ``\\frac{1}{1+e^{x}``) makes LaTeX run
    away to the end of the file hunting for the closer, dropping every question
    after it.  Balancing each math fragment makes that impossible.
    """
    out: list[str] = []
    depth = 0
    i, n = 0, len(c)
    while i < n:
        ch = c[i]
        if ch == "\\" and i + 1 < n:
            out.append(c[i : i + 2])  # escaped char (incl. \{ \} \\) -> not a group
            i += 2
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            if depth == 0:
                out.append("\\}")  # stray closer -> escape instead of "too many }"
                i += 1
                continue
            depth -= 1
        out.append(ch)
        i += 1
    if depth > 0:
        out.append("}" * depth)
    return "".join(out)


def _balance_environments(c: str) -> str:
    """Close unclosed math environments.

    A bare ``\\begin{pmatrix}`` / ``\\begin{align*}`` with no matching ``\\end``
    makes LaTeX run away to the end of the document.  Append the missing
    ``\\end{...}`` (innermost first) so the damage cannot escape the fragment.
    """
    if "\\begin{" not in c:
        return c
    stack: list[str] = []
    for kind, name in re.findall(r"\\(begin|end)\{([a-zA-Z*]+)\}", c):
        if kind == "begin":
            stack.append(name)
        elif stack and stack[-1] == name:
            stack.pop()
        elif name in stack:  # close inner envs until the match
            while stack and stack.pop() != name:
                pass
    if not stack:
        return c
    return c + "".join(f"\\end{{{name}}}" for name in reversed(stack))


_TEXT_CMD_RE = re.compile(
    r"\\(?:text|texttt|textbf|textit|textsf|textrm|textsc|emph|mbox)\{"
)


def _escape_text_cmd_args(c: str) -> str:
    """Escape raw _ ^ & inside \\text-family arguments.

    In math mode ``\\texttt``/``\\text`` switch their argument to text mode, where
    a raw ``_`` / ``^`` / ``&`` is illegal ("Missing $ inserted") — exactly what
    a model-written ``$\\texttt{emp_id}$`` triggers.  Escaping them keeps the
    identifier literal and compilable.
    """
    if "\\text" not in c and "\\emph" not in c and "\\mbox" not in c:
        return c
    result: list[str] = []
    i, n = 0, len(c)
    while i < n:
        m = _TEXT_CMD_RE.match(c, i)
        if not m:
            result.append(c[i])
            i += 1
            continue
        depth, j = 1, m.end()
        while j < n and depth:
            if c[j] == "\\":
                j += 2
                continue
            if c[j] == "{":
                depth += 1
            elif c[j] == "}":
                depth -= 1
            j += 1
        arg_end = j - 1 if depth == 0 else j
        arg = c[m.end() : arg_end]
        arg = re.sub(r"(?<!\\)_", r"\\_", arg)
        arg = re.sub(r"(?<!\\)\^", r"\\textasciicircum{}", arg)
        arg = re.sub(r"(?<!\\)&", r"\\&", arg)
        result.append(c[i : m.end()])
        result.append(arg)
        if depth == 0:
            result.append("}")
        i = j
    return "".join(result)


def _convert_display_envs(c: str) -> str:
    """Map display-only math environments to nestable equivalents.

    ``align``/``gather``/... are top-level display environments and are illegal
    nested inside other math (e.g. a model-written ``align*`` inside ``aligned``
    inside ``\\[ \\]``).  ``aligned``/``gathered`` behave the same but nest legally.
    """
    if "\\begin{" not in c:
        return c
    c = re.sub(r"\\(begin|end)\{align\*?\}", r"\\\g<1>{aligned}", c)
    c = re.sub(r"\\(begin|end)\{gather\*?\}", r"\\\g<1>{gathered}", c)
    c = re.sub(
        r"\\(begin|end)\{(?:eqnarray|multline|flalign|alignat)\*?\}",
        r"\\\g<1>{aligned}",
        c,
    )
    c = re.sub(r"\\begin\{displaymath\}|\\end\{displaymath\}", "", c)
    c = re.sub(r"(\\begin\{aligned\})\s*\{\d+\}", r"\1", c)  # drop alignat arg
    return c


def _clean_math(content: str) -> str:
    c = _fix_over_escaped(content)
    c = _strip_math_dollars(c)
    c = _convert_display_envs(c)
    c = _escape_text_cmd_args(c)
    c = _protect_math(_apply_unicode_math(c)).strip()
    c = _balance_braces(c)
    return _balance_environments(c)


def _emit_inline(content: str) -> str:
    c = _clean_math(content)
    if not c:
        return ""
    # \\ and & are illegal in inline math -> promote to a display block.
    if "\\\\" in c or "&" in c:
        return _emit_display(content)
    return "$" + c + "$"


def _emit_display(content: str) -> str:
    c = _clean_math(content)
    if not c:
        return ""

    env = re.match(r"\\begin\{([a-zA-Z]+)\*?\}", c)
    if env and env.group(1) in _DISPLAY_ENVS:
        # Already a standalone display environment (align, gather, ...).
        return "\n" + c + "\n"
    if _SUB_MATH_ENV_RE.search(c):
        # Contains aligned/cases/matrix/... -> needs surrounding math mode only.
        return "\n\\[\n" + c + "\n\\]\n"
    if "\\\\" in c or "&" in c:
        # Bare line breaks / alignment -> wrap in aligned so they are legal.
        return "\n\\[\n\\begin{aligned}\n" + c + "\n\\end{aligned}\n\\]\n"
    return "\n\\[ " + c + " \\]\n"


def _emit_inline_line(line: str) -> str:
    """Render a single newline-free line (text + inline $...$)."""
    out: list[str] = []
    i, n = 0, len(line)
    while i < n:
        if line[i] == "$":
            end = line.find("$", i + 1)
            if end == -1:  # unbalanced -> treat the $ as literal text
                out.append(_emit_text_run(line[i:]))
                break
            out.append(_emit_inline(line[i + 1 : end]))
            i = end + 1
            continue
        nxt = line.find("$", i)
        run = line[i:] if nxt == -1 else line[i:nxt]
        out.append(_emit_text_run(run))
        i = n if nxt == -1 else nxt
    return "".join(out)


def _emit_text_run(s: str) -> str:
    out = _apply_unicode_text(_escape_text(s))
    # Markdown bold markers leak in from the model; drop the asterisks so they
    # do not render as literal "**".
    if "**" in out:
        out = out.replace("**", "")
    return out


def _split_display_blocks(text: str) -> list[tuple[str, str]]:
    """Split into ('display', inner) and ('text', chunk); unbalanced $$ stays text."""
    blocks: list[tuple[str, str]] = []
    buf: list[str] = []
    i, n = 0, len(text)
    while i < n:
        if text[i] == "$" and i + 1 < n and text[i + 1] == "$":
            end = text.find("$$", i + 2)
            if end == -1:
                buf.append(text[i:])
                i = n
                break
            if buf:
                blocks.append(("text", "".join(buf)))
                buf = []
            blocks.append(("display", text[i + 2 : end]))
            i = end + 2
            continue
        buf.append(text[i])
        i += 1
    if buf:
        blocks.append(("text", "".join(buf)))
    return blocks


def _emit_text_block(content: str, solution_layout: bool) -> str:
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    if not content.strip():
        return ""

    if solution_layout:
        # One paragraph per line -> clean step-by-step layout, never any "\\".
        paragraphs = [ln.strip() for ln in re.split(r"\n+", content) if ln.strip()]
    else:
        paragraphs = []
        for block in re.split(r"\n{2,}", content):
            joined = " ".join(ln.strip() for ln in block.split("\n") if ln.strip())
            if joined:
                paragraphs.append(joined)

    rendered = [_emit_inline_line(p) for p in paragraphs]
    rendered = [r for r in rendered if r.strip()]
    if not rendered:
        return ""
    return "\n\n".join(rendered) + "\n\n"


def render_mixed_latex(raw: str | None, *, solution_layout: bool = False) -> str:
    """
    Convert a question/solution/choice string into clean, compile-safe LaTeX.

    ``solution_layout=True`` renders each line as its own paragraph, which is
    ideal for step-by-step solutions.
    """
    if raw is None:
        return ""
    text = str(raw)
    if not text.strip():
        return ""

    prepared = _prepare(text)
    out: list[str] = []
    for kind, content in _split_display_blocks(prepared):
        if kind == "display":
            out.append(_emit_display(content))
        else:
            out.append(_emit_text_block(content, solution_layout))

    result = "".join(out)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return _final_safety(result.strip())


def _brace_net(s: str) -> int:
    depth = 0
    i, n = 0, len(s)
    while i < n:
        if s[i] == "\\":
            i += 2
            continue
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
        i += 1
    return depth


def _final_safety(s: str) -> str:
    """Last-resort guard so a single field can never break the whole document.

    Per-fragment cleaning already balances braces and pairs '$', so this should
    rarely change anything; it only contains damage from any unforeseen input.
    An extra '}' (net < 0) is harmless to LaTeX, but a missing '}' (net > 0)
    would run away, so close those.  An odd '$' would bleed math mode, so escape
    the straggler.
    """
    net = _brace_net(s)
    if net > 0:
        s = s + ("}" * net)
    positions = [m.start() for m in re.finditer(r"(?<!\\)\$", s)]
    if len(positions) % 2 == 1:
        i = positions[-1]
        s = s[:i] + "\\$" + s[i + 1 :]
    return s
