"""
Vision-based PYQ extractor: official GATE PDFs -> canonical data/pyq/json/{PAPER}_{YEAR}.json.

Pipeline (per paper-year):
  1. Render the question-paper PDF pages to images (PyMuPDF).
  2. A vision LLM extracts each question as JSON, tagging section/topic from the
     syllabus and folding figures into the stem as "[Figure: ...]" (skipping
     questions whose figure cannot be described in text).
  3. The answer-key PDF is parsed (vision) into {qno: answer} and merged.
  4. The merged, validated result is written as the canonical JSON for review.

This is the costly/reviewable step. ALWAYS spot-check the produced JSON before
running `scripts/load_pyq.py`. It calls a vision model, so it uses credits — pilot
on one paper first and tune the prompt/model as needed.

Naming convention (files go in data/pyq/pdfs/):
    {PAPER}_{YEAR}_questions.pdf     e.g. CS_2024_questions.pdf, DA_2023_questions.pdf
    {PAPER}_{YEAR}_answerkey.pdf     e.g. CS_2024_answerkey.pdf, DA_2023_answerkey.pdf
where PAPER is CS or DA. Year comes from the filename.

Usage (from backend/):
    # one paper-year:
    python scripts/extract_pyq.py --paper DA --year 2024 --vision-model <vl-model>
    # EVERY *_questions.pdf found in data/pyq/pdfs/ (recommended for many papers):
    python scripts/extract_pyq.py --all --vision-model <vl-model>

Heavy imports (PyMuPDF, openai) are lazy so this file loads even before they are
installed. Install with: pip install pymupdf openai
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import re
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import settings
from app.services.llm_service import extract_json_array, extract_json_object

PDF_DIR = BACKEND_ROOT / "data" / "pyq" / "pdfs"
JSON_DIR = BACKEND_ROOT / "data" / "pyq" / "json"
SYLLABUS_DIR = BACKEND_ROOT / "data" / "syllabus"

PAPER_NAMES = {
    "CS": "Computer Science and Information Technology",
    "DA": "Data Science and Artificial Intelligence",
}

_QPDF_RE = re.compile(r"^(CS|DA)_(\d{4})_questions\.pdf$", re.IGNORECASE)

_EXTRACT_SYSTEM = (
    "You are extracting questions from an official GATE exam page image. "
    "Return ONLY a JSON array of question objects; no prose. Each object: "
    "qno (int), section_name (string), topic (string), question_type "
    "(\"MCQ\"|\"MSQ\"|\"NAT\"), marks (1|2), stem (string, LaTeX for math), "
    "code_snippet (string|null), has_figure (bool), options (array of 4 strings "
    "for MCQ/MSQ, else null). Rules: do NOT include answers. Fold any figure into "
    "the stem as \"[Figure: <precise description>]\" and set has_figure=true. If a "
    "figure cannot be faithfully described in text, set \"skip\": true on that "
    "object. Assign section_name and topic from the provided syllabus list. Ignore "
    "headers, footers, and instructions."
)

_ANSWERS_SYSTEM = (
    "You are reading an official GATE answer key. Return ONLY a JSON object mapping "
    "question number (as a string) to the answer. For MCQ use the option letter "
    "(\"A\"-\"D\"); for MSQ use comma-joined letters (\"A,C\"); for NAT use the "
    "numeric value or stated range as a string. Example: {\"1\": \"C\", \"2\": \"A,D\", "
    "\"3\": \"7.5\"}. No prose."
)


def _syllabus_topics(paper: str) -> str:
    """Flat 'Section :: Topic' lines from the syllabus, for tagging context."""
    lines: list[str] = []
    if SYLLABUS_DIR.exists():
        target = f"{paper}_syllabus.json".lower()
        for p in SYLLABUS_DIR.iterdir():
            if p.is_file() and p.name.lower() == target:
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                    for sec in data.get("sections", []):
                        name = sec.get("section_name", "")
                        for topic in sec.get("topics", []):
                            lines.append(f"{name} :: {topic}")
                except (json.JSONDecodeError, OSError):
                    pass
                break
    return "\n".join(lines)


def _render_pdf(pdf_path: Path, max_pages: int | None) -> list[bytes]:
    import fitz  # PyMuPDF (lazy)

    doc = fitz.open(str(pdf_path))
    images: list[bytes] = []
    matrix = fitz.Matrix(2, 2)  # ~144 DPI for legible small text
    for i, page in enumerate(doc):
        if max_pages is not None and i >= max_pages:
            break
        images.append(page.get_pixmap(matrix=matrix).tobytes("png"))
    doc.close()
    return images


def _vision_client(api_key: str, base_url: str | None):
    from openai import AsyncOpenAI  # lazy

    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return AsyncOpenAI(**kwargs)


async def _vision_call(client, model: str, system: str, text: str, png: bytes) -> str:
    b64 = base64.b64encode(png).decode("ascii")
    resp = await client.chat.completions.create(
        model=model,
        temperature=0.1,
        messages=[
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                    {"type": "image_url",
                     "image_url": {"url": f"data:image/png;base64,{b64}"}},
                ],
            },
        ],
    )
    return resp.choices[0].message.content or ""


async def _extract_questions(client, model, pages, paper, year, syllabus) -> list[dict]:
    questions: list[dict] = []
    user = (
        f"Paper: {paper} ({PAPER_NAMES.get(paper, paper)}), Year: {year}.\n"
        f"Syllabus (Section :: Topic):\n{syllabus}\n\n"
        "Extract all complete questions on this page as a JSON array."
    )
    for idx, png in enumerate(pages, 1):
        try:
            raw = await _vision_call(client, model, _EXTRACT_SYSTEM, user, png)
            page_qs = extract_json_array(raw)
        except Exception as exc:  # noqa: BLE001
            print(f"    ! page {idx}: extraction failed: {exc}")
            continue
        kept = [q for q in page_qs if not q.get("skip")]
        questions.extend(kept)
        print(f"    page {idx}: +{len(kept)} question(s)")
    return questions


async def _extract_answers(client, model, pages) -> dict:
    answers: dict = {}
    for idx, png in enumerate(pages, 1):
        try:
            raw = await _vision_call(
                client, model, _ANSWERS_SYSTEM,
                "Read this answer-key page and return the qno->answer JSON object.",
                png,
            )
            answers.update(extract_json_object(raw))
        except Exception as exc:  # noqa: BLE001
            print(f"    ! answer-key page {idx}: {exc}")
    return answers


def _merge_answer(q: dict, raw_answer: str | None) -> None:
    """Attach a parsed answer to a question record in the canonical shape."""
    q.setdefault("code_language", None)
    q.setdefault("solution", None)
    q["answer"] = None
    q["answer_value"] = None
    q["tolerance"] = None
    if raw_answer is None:
        return
    raw_answer = str(raw_answer).strip()
    if q.get("question_type") == "NAT":
        try:
            q["answer_value"] = float(raw_answer)
            q["tolerance"] = 0.0
        except ValueError:
            q["answer_value"] = None
    else:
        q["answer"] = raw_answer.upper().replace(" ", "")


def _discover_pairs() -> list[tuple[str, int, Path, Path]]:
    """Find every {PAPER}_{YEAR}_questions.pdf in pdfs/ and its answer-key pair."""
    pairs: list[tuple[str, int, Path, Path]] = []
    if not PDF_DIR.exists():
        return pairs
    for p in sorted(PDF_DIR.glob("*_questions.pdf")):
        m = _QPDF_RE.match(p.name)
        if not m:
            print(f"  (skipping unrecognised filename: {p.name})")
            continue
        paper = m.group(1).upper()
        year = int(m.group(2))
        a_pdf = PDF_DIR / f"{paper}_{year}_answerkey.pdf"
        pairs.append((paper, year, p, a_pdf))
    return pairs


async def _process_one(
    client, model, paper, year, q_pdf: Path, a_pdf: Path, max_pages, syllabus
) -> dict:
    out_path = JSON_DIR / f"{paper}_{year}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n=== {paper} {year} ===")
    print(f"  rendering {q_pdf.name} ...")
    q_pages = _render_pdf(q_pdf, max_pages)
    print(f"  extracting from {len(q_pages)} page(s) with {model} ...")
    questions = await _extract_questions(client, model, q_pages, paper, year, syllabus)

    answers: dict = {}
    if a_pdf.exists():
        print(f"  reading answer key {a_pdf.name} ...")
        answers = await _extract_answers(client, model, _render_pdf(a_pdf, max_pages))
    else:
        print(f"  (no answer key at {a_pdf.name}; answers left blank)")

    for q in questions:
        _merge_answer(q, answers.get(str(q.get("qno"))))
        q.pop("skip", None)

    payload = {
        "paper": paper,
        "year": year,
        "doc_type": "PYQ",
        "source": f"GATE {year} {paper} official question paper + answer key",
        "questions": questions,
    }
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  wrote {len(questions)} question(s) -> {out_path.name}")
    return {"paper": paper, "year": year, "questions": len(questions), "out": out_path.name}


async def main() -> None:
    parser = argparse.ArgumentParser(description="Extract PYQs from official GATE PDFs.")
    parser.add_argument("--all", action="store_true",
                        help="Process every {PAPER}_{YEAR}_questions.pdf in data/pyq/pdfs/.")
    parser.add_argument("--paper", choices=["CS", "DA"])
    parser.add_argument("--year", type=int)
    parser.add_argument("--questions-pdf", default=None)
    parser.add_argument("--answerkey-pdf", default=None)
    parser.add_argument("--vision-model", default=settings.VISION_MODEL)
    parser.add_argument("--api-key", default=settings.NEBIUS_API_KEY)
    parser.add_argument("--base-url", default=settings.NEBIUS_BASE_URL)
    parser.add_argument("--max-pages", type=int, default=None)
    args = parser.parse_args()

    if not args.vision_model:
        raise SystemExit(
            "No vision model set. Pass --vision-model or set VISION_MODEL in .env "
            "(e.g. a Nebius VL model like Qwen/Qwen2.5-VL-72B-Instruct)."
        )
    if not args.all and not (args.paper and args.year):
        raise SystemExit("Specify --all, or both --paper and --year.")

    client = _vision_client(args.api_key, args.base_url)
    syllabus_cache: dict[str, str] = {}

    def syllabus_for(paper: str) -> str:
        if paper not in syllabus_cache:
            syllabus_cache[paper] = _syllabus_topics(paper)
        return syllabus_cache[paper]

    if args.all:
        pairs = _discover_pairs()
        if not pairs:
            raise SystemExit(f"No '*_questions.pdf' files found in {PDF_DIR}")
        print(f"Found {len(pairs)} paper(s): " +
              ", ".join(f"{p}_{y}" for p, y, _, _ in pairs))
        summaries: list[dict] = []
        errors: list[str] = []
        for paper, year, q_pdf, a_pdf in pairs:
            try:
                summaries.append(await _process_one(
                    client, args.vision_model, paper, year, q_pdf, a_pdf,
                    args.max_pages, syllabus_for(paper),
                ))
            except Exception as exc:  # noqa: BLE001
                print(f"  ! {paper} {year} failed: {exc}")
                errors.append(f"{paper}_{year}: {exc}")
        print("\n===== Batch summary =====")
        for s in summaries:
            print(f"  {s['paper']} {s['year']}: {s['questions']} questions -> {s['out']}")
        if errors:
            print("  errors:")
            for e in errors:
                print(f"    - {e}")
        print(f"  TOTAL: {sum(s['questions'] for s in summaries)} questions "
              f"across {len(summaries)} paper(s)")
    else:
        q_pdf = Path(args.questions_pdf or PDF_DIR / f"{args.paper}_{args.year}_questions.pdf")
        a_pdf = Path(args.answerkey_pdf or PDF_DIR / f"{args.paper}_{args.year}_answerkey.pdf")
        if not q_pdf.exists():
            raise SystemExit(f"Question PDF not found: {q_pdf}")
        await _process_one(
            client, args.vision_model, args.paper, args.year,
            q_pdf, a_pdf, args.max_pages, syllabus_for(args.paper),
        )

    print("\nREVIEW the JSON in data/pyq/json/, then run: python scripts/load_pyq.py")


if __name__ == "__main__":
    asyncio.run(main())
