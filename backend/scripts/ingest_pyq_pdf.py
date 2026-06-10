#!/usr/bin/env python3
"""
Offline GATE PYQ (previous-year-question) PDF → structured JSON extractor.

Renders each PDF page to PNG (PyMuPDF), sends page batches to a vision-capable
Claude model, and writes a reviewed-by-hand JSON file that the backend's
`load_pyqs` loader (POST /api/v1/admin/load-data) ingests into pyq_questions.

Standalone by design: NO imports from the FastAPI app. Run it from any venv
that has the deps in scripts/requirements-ingest.txt and ANTHROPIC_API_KEY set.

Usage:
    python ingest_pyq_pdf.py --pdf CS_2024.pdf --paper CS --year 2024 \
        [--answer-key-pdf CS_2024_key.pdf] [--out ../data/pyqs] \
        [--pages-per-call 3] [--dpi 170] [--model claude-opus-4-8] [--no-resume]

Each vision call is checkpointed under <out>/.checkpoints/<PAPER>_<YEAR>/ so a
killed/failed run only re-pays the missing chunks on the next invocation.
"""

import argparse
import base64
import json
import re
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit(
        "PyMuPDF is required. Install script dependencies first:\n"
        "    pip install -r requirements-ingest.txt"
    )

try:
    import anthropic
except ImportError:
    sys.exit(
        "The anthropic package is required. Install script dependencies first:\n"
        "    pip install -r requirements-ingest.txt"
    )

DEFAULT_MODEL = "claude-opus-4-8"
MAX_OUTPUT_TOKENS = 32000

VALID_TYPES = {"MCQ", "MSQ", "NAT"}
MCQ_ANSWER_RE = re.compile(r"^[A-D]$")
MSQ_ANSWER_RE = re.compile(r"^[A-D](;[A-D]){0,3}$")
NAT_RANGE_RE = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s+to\s+(-?\d+(?:\.\d+)?)\s*$", re.I)


# ──────────────────────────────────────────────────────────
# Structured-output JSON schemas
# (structured outputs require additionalProperties: false on every object and
# do not support array-length constraints — option count is validated locally)
# ──────────────────────────────────────────────────────────

def _nullable(json_type: str) -> dict:
    return {"anyOf": [{"type": json_type}, {"type": "null"}]}


QUESTION_SCHEMA = {
    "type": "object",
    "properties": {
        "qno": {"type": "integer"},
        "question_type": {"type": "string", "enum": sorted(VALID_TYPES)},
        "marks": {"type": "integer", "enum": [1, 2]},
        "section_name": {"type": "string"},
        "topic": {"type": "string"},
        "stem": {"type": "string"},
        "code_snippet": _nullable("string"),
        "options": {
            "anyOf": [
                {"type": "array", "items": {"type": "string"}},
                {"type": "null"},
            ]
        },
        "answer": _nullable("string"),
        "answer_value": _nullable("number"),
        "tolerance": _nullable("number"),
        "solution": _nullable("string"),
        "truncated": {"type": "boolean"},
    },
    "required": [
        "qno", "question_type", "marks", "section_name", "topic", "stem",
        "code_snippet", "options", "answer", "answer_value", "tolerance",
        "solution", "truncated",
    ],
    "additionalProperties": False,
}

CHUNK_SCHEMA = {
    "type": "object",
    "properties": {
        "questions": {"type": "array", "items": QUESTION_SCHEMA},
    },
    "required": ["questions"],
    "additionalProperties": False,
}

ANSWER_KEY_SCHEMA = {
    "type": "object",
    "properties": {
        "answers": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "qno": {"type": "integer"},
                    "answer": {"type": "string"},
                },
                "required": ["qno", "answer"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["answers"],
    "additionalProperties": False,
}


# ──────────────────────────────────────────────────────────
# Prompts
# ──────────────────────────────────────────────────────────

EXTRACTION_SYSTEM_PROMPT = """\
You are extracting questions from scanned pages of an official GATE {paper} \
{year} question paper. Return JSON matching the provided schema exactly.

RULES:
1. Extract EVERY question that BEGINS on these pages. If a question continues
   onto a page you cannot see, extract what is visible and set "truncated" to
   true; otherwise set it to false.
2. "qno" is the printed question number. "question_type": MCQ has exactly one
   correct option; MSQ is marked "one or more correct"; NAT has a numerical
   answer and no options. "marks": 1 or 2, read from the paper's marking text
   or section header.
3. "section_name": "General Aptitude" for the GA section; otherwise the
   subject area (e.g. "Algorithms", "Operating Systems", "Linear Algebra").
   "topic": the specific concept the question tests.
4. Transcribe ALL mathematics as LaTeX using $...$ inline delimiters. Put any
   code verbatim in "code_snippet" (not in "stem"); otherwise code_snippet is
   null.
5. FIGURES/DIAGRAMS: never skip a question because it has a figure. Embed a
   precise textual description inside the stem at the figure's position, e.g.
   "[Figure: directed graph with 5 nodes A-E; edges A->B (weight 2), ...]".
   The description must capture every detail needed to solve the question.
6. Options: exactly the 4 printed option texts (without their A/B/C/D labels),
   in printed order. null for NAT.
7. If the correct answer is printed on these pages, fill "answer" (MCQ: "A".."D";
   MSQ: letters joined with ";", e.g. "A;C"; NAT: also set "answer_value" and
   "tolerance"). Otherwise leave answer fields null.
8. Never invent questions, never merge two questions into one, never reword
   the original text beyond LaTeX/figure transcription.
"""

CHUNK_USER_PROMPT = (
    "These images are pages {lo}-{hi} (1-based) of the GATE {paper} {year} "
    "question paper. Extract all questions that begin on these pages."
)

ANSWER_KEY_SYSTEM_PROMPT = """\
You are extracting the official answer key of the GATE {paper} {year} paper
from scanned pages. Return JSON matching the provided schema exactly.

For each question number visible on these pages, output its answer as printed:
- MCQ: the single option letter, e.g. "A"
- MSQ: all correct letters joined with ";", e.g. "A;C"
- NAT: the printed value or range verbatim, e.g. "0.25" or "0.24 to 0.26"
Do not invent answers for question numbers that are not visible.
"""

ANSWER_KEY_USER_PROMPT = (
    "These images are pages {lo}-{hi} (1-based) of the answer-key document "
    "for GATE {paper} {year}. Extract every (question number, answer) pair."
)


# ──────────────────────────────────────────────────────────
# PDF rendering and chunking
# ──────────────────────────────────────────────────────────

def render_pdf_pages(pdf_path: Path, dpi: int) -> list[bytes]:
    """Render every page of the PDF to PNG bytes."""
    doc = fitz.open(pdf_path)
    try:
        return [page.get_pixmap(dpi=dpi).tobytes("png") for page in doc]
    finally:
        doc.close()


def chunk_ranges(n_pages: int, per_call: int) -> list[tuple[int, int]]:
    """Split [0, n_pages) into windows of `per_call` pages with 1-page overlap,
    so a question starting at a chunk boundary is fully visible to at least one
    call (duplicates are merged by qno later)."""
    step = max(1, per_call - 1)
    ranges: list[tuple[int, int]] = []
    start = 0
    while start < n_pages:
        end = min(start + per_call, n_pages)
        ranges.append((start, end))
        if end == n_pages:
            break
        start += step
    return ranges


def image_block(png_bytes: bytes) -> dict:
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/png",
            "data": base64.standard_b64encode(png_bytes).decode("utf-8"),
        },
    }


# ──────────────────────────────────────────────────────────
# Vision calls
# ──────────────────────────────────────────────────────────

def _call_vision(
    client: "anthropic.Anthropic",
    model: str,
    system_prompt: str,
    user_text: str,
    pngs: list[bytes],
    schema: dict,
) -> dict:
    """One streamed vision call with a structured-output schema. Returns the
    parsed JSON object. Streaming protects long extractions from HTTP timeouts."""
    content = [image_block(p) for p in pngs]
    content.append({"type": "text", "text": user_text})

    with client.messages.stream(
        model=model,
        max_tokens=MAX_OUTPUT_TOKENS,
        thinking={"type": "adaptive"},
        system=system_prompt,
        messages=[{"role": "user", "content": content}],
        output_config={"format": {"type": "json_schema", "schema": schema}},
    ) as stream:
        message = stream.get_final_message()

    if message.stop_reason == "max_tokens":
        print(
            "  WARNING: output hit the max_tokens cap; this chunk may be "
            "incomplete. Consider lowering --pages-per-call.",
            file=sys.stderr,
        )
    text = next(b.text for b in message.content if b.type == "text")
    return json.loads(text)


def extract_chunk(client, model, pngs, paper, year, page_lo, page_hi) -> list[dict]:
    data = _call_vision(
        client,
        model,
        EXTRACTION_SYSTEM_PROMPT.format(paper=paper, year=year),
        CHUNK_USER_PROMPT.format(lo=page_lo, hi=page_hi, paper=paper, year=year),
        pngs,
        CHUNK_SCHEMA,
    )
    return data["questions"]


def extract_answer_key_chunk(client, model, pngs, paper, year, page_lo, page_hi) -> dict[int, str]:
    data = _call_vision(
        client,
        model,
        ANSWER_KEY_SYSTEM_PROMPT.format(paper=paper, year=year),
        ANSWER_KEY_USER_PROMPT.format(lo=page_lo, hi=page_hi, paper=paper, year=year),
        pngs,
        ANSWER_KEY_SCHEMA,
    )
    return {entry["qno"]: entry["answer"] for entry in data["answers"]}


# ──────────────────────────────────────────────────────────
# Merge / answer key / validation
# ──────────────────────────────────────────────────────────

def _completeness(q: dict) -> tuple:
    """Sort key: prefer untruncated, then answered, then with options, then
    the longest stem (chunk overlap produces duplicate qno entries)."""
    return (
        not q.get("truncated", False),
        q.get("answer") is not None,
        q.get("options") is not None,
        len(q.get("stem") or ""),
    )


def merge_chunks(chunks: list[list[dict]]) -> list[dict]:
    best: dict[int, dict] = {}
    for chunk in chunks:
        for q in chunk:
            qno = q.get("qno")
            if not isinstance(qno, int):
                continue
            if qno not in best or _completeness(q) > _completeness(best[qno]):
                best[qno] = q
    return [best[qno] for qno in sorted(best)]


def normalize_answer(raw: str, question_type: str) -> dict:
    """Normalize a printed answer-key string into answer/answer_value/tolerance."""
    raw = (raw or "").strip()
    result: dict = {"answer": raw[:50] or None, "answer_value": None, "tolerance": None}

    if question_type in ("MCQ", "MSQ"):
        letters = re.split(r"[;,\s]+", raw.upper())
        letters = [l for l in letters if MCQ_ANSWER_RE.match(l)]
        result["answer"] = ";".join(dict.fromkeys(letters)) or None
        return result

    # NAT: a single value or a "low to high" range
    range_match = NAT_RANGE_RE.match(raw)
    if range_match:
        lo, hi = float(range_match.group(1)), float(range_match.group(2))
        result["answer_value"] = round((lo + hi) / 2, 6)
        result["tolerance"] = round(abs(hi - lo) / 2, 6)
        return result
    try:
        result["answer_value"] = float(raw)
        result["tolerance"] = 0.01
    except ValueError:
        pass
    return result


def apply_answer_key(questions: list[dict], key: dict[int, str]) -> None:
    for q in questions:
        raw = key.get(q.get("qno"))
        if raw is None:
            continue
        normalized = normalize_answer(raw, q.get("question_type", ""))
        q["answer"] = normalized["answer"]
        if q.get("question_type") == "NAT":
            q["answer_value"] = normalized["answer_value"]
            q["tolerance"] = normalized["tolerance"]


def validate_question(q: dict) -> list[str]:
    """Returns error strings; [] means valid. Mirrors the backend loader's
    light validation so review-time surprises are caught here first."""
    errors: list[str] = []
    if not isinstance(q.get("qno"), int):
        errors.append("qno must be an integer")
    qtype = q.get("question_type")
    if qtype not in VALID_TYPES:
        errors.append(f"question_type must be one of {sorted(VALID_TYPES)}")
    if q.get("marks") not in (1, 2):
        errors.append("marks must be 1 or 2")
    stem = q.get("stem")
    if not isinstance(stem, str) or not stem.strip():
        errors.append("stem must be a non-empty string")
    options = q.get("options")
    if qtype in ("MCQ", "MSQ"):
        if not isinstance(options, list) or len(options) != 4:
            errors.append("MCQ/MSQ questions need exactly 4 options")
    elif qtype == "NAT" and options:
        errors.append("NAT questions must not have options")
    answer = q.get("answer")
    if answer is not None:
        if not isinstance(answer, str) or len(answer) > 50:
            errors.append("answer must be a string of at most 50 characters")
        elif qtype == "MCQ" and not MCQ_ANSWER_RE.match(answer):
            errors.append("MCQ answer must match ^[A-D]$")
        elif qtype == "MSQ" and not MSQ_ANSWER_RE.match(answer):
            errors.append("MSQ answer must match ^[A-D](;[A-D]){0,3}$")
    if q.get("answer_value") is not None and not isinstance(
        q["answer_value"], (int, float)
    ):
        errors.append("answer_value must be numeric")
    if q.get("truncated"):
        errors.append("question is truncated (no chunk saw it in full)")
    return errors


# ──────────────────────────────────────────────────────────
# Checkpointing
# ──────────────────────────────────────────────────────────

def checkpoint_path(ckpt_dir: Path, name: str) -> Path:
    return ckpt_dir / f"{name}.json"


def load_checkpoint(path: Path):
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return None


def save_checkpoint(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


# ──────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract GATE PYQs from a PDF into backend/data/pyqs JSON."
    )
    parser.add_argument("--pdf", required=True, type=Path, help="Question-paper PDF")
    parser.add_argument("--paper", required=True, choices=["CS", "DA"])
    parser.add_argument("--year", required=True, type=int)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data" / "pyqs",
        help="Output directory (default: backend/data/pyqs)",
    )
    parser.add_argument("--answer-key-pdf", type=Path, default=None)
    parser.add_argument("--pages-per-call", type=int, default=3)
    parser.add_argument("--dpi", type=int, default=170)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Ignore existing checkpoints and re-extract everything",
    )
    args = parser.parse_args()

    if not args.pdf.exists():
        sys.exit(f"PDF not found: {args.pdf}")
    if args.answer_key_pdf and not args.answer_key_pdf.exists():
        sys.exit(f"Answer-key PDF not found: {args.answer_key_pdf}")

    client = anthropic.Anthropic()  # needs ANTHROPIC_API_KEY in the environment
    ckpt_dir = args.out / ".checkpoints" / f"{args.paper}_{args.year}"

    # ── 1. Render + extract question pages ──
    print(f"Rendering {args.pdf.name} at {args.dpi} DPI ...")
    pages = render_pdf_pages(args.pdf, args.dpi)
    ranges = chunk_ranges(len(pages), args.pages_per_call)
    print(f"{len(pages)} pages -> {len(ranges)} vision calls (1-page overlap)")

    chunks: list[list[dict]] = []
    for i, (lo, hi) in enumerate(ranges):
        ckpt = checkpoint_path(ckpt_dir, f"chunk_{i:03d}")
        cached = None if args.no_resume else load_checkpoint(ckpt)
        if cached is not None:
            print(f"  chunk {i + 1}/{len(ranges)} (pages {lo + 1}-{hi}): checkpoint hit")
            chunks.append(cached)
            continue
        print(f"  chunk {i + 1}/{len(ranges)} (pages {lo + 1}-{hi}): extracting ...")
        questions = extract_chunk(
            client, args.model, pages[lo:hi], args.paper, args.year, lo + 1, hi
        )
        save_checkpoint(ckpt, questions)
        chunks.append(questions)
        print(f"    -> {len(questions)} question(s)")

    questions = merge_chunks(chunks)
    print(f"Merged: {len(questions)} unique question(s) by qno")

    # ── 2. Optional answer-key pass ──
    if args.answer_key_pdf:
        ckpt = checkpoint_path(ckpt_dir, "answer_key")
        cached = None if args.no_resume else load_checkpoint(ckpt)
        if cached is not None:
            print("Answer key: checkpoint hit")
            key = {int(k): v for k, v in cached.items()}
        else:
            print(f"Extracting answer key from {args.answer_key_pdf.name} ...")
            key_pages = render_pdf_pages(args.answer_key_pdf, args.dpi)
            key: dict[int, str] = {}
            for lo, hi in chunk_ranges(len(key_pages), args.pages_per_call):
                key.update(
                    extract_answer_key_chunk(
                        client, args.model, key_pages[lo:hi],
                        args.paper, args.year, lo + 1, hi,
                    )
                )
            save_checkpoint(ckpt, {str(k): v for k, v in key.items()})
        apply_answer_key(questions, key)
        print(f"Answer key applied: {len(key)} answer(s)")

    # ── 3. Validate, drop invalid, write output ──
    valid: list[dict] = []
    dropped: list[tuple[int | None, list[str]]] = []
    for q in questions:
        errors = validate_question(q)
        if errors:
            dropped.append((q.get("qno"), errors))
        else:
            q.pop("truncated", None)  # internal-only field
            valid.append(q)

    output = {
        "paper": args.paper,
        "year": args.year,
        "source_filename": args.pdf.name,
        "extracted_with": args.model,
        "questions": valid,
    }
    args.out.mkdir(parents=True, exist_ok=True)
    out_path = args.out / f"{args.paper}_{args.year}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # ── 4. Summary for human review ──
    by_type: dict[str, int] = {}
    by_marks: dict[int, int] = {}
    unanswered = 0
    for q in valid:
        by_type[q["question_type"]] = by_type.get(q["question_type"], 0) + 1
        by_marks[q["marks"]] = by_marks.get(q["marks"], 0) + 1
        if q["answer"] is None and q["answer_value"] is None:
            unanswered += 1
    print("\n==== Summary ====")
    print(f"Written:    {out_path}  ({len(valid)} questions)")
    print(f"By type:    {by_type}")
    print(f"By marks:   {by_marks}")
    print(f"Unanswered: {unanswered}")
    if dropped:
        print(f"Dropped:    {len(dropped)} question(s):")
        for qno, errors in dropped:
            print(f"  q{qno}: {'; '.join(errors)}")
    qnos = [q["qno"] for q in valid]
    gaps = sorted(set(range(min(qnos), max(qnos) + 1)) - set(qnos)) if qnos else []
    if gaps:
        print(f"Missing qno(s): {gaps}  <- review the PDF around these")
    print(
        "\nReview the JSON by hand, then load it via "
        "POST /api/v1/admin/load-data (it reads backend/data/pyqs/*.json)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
