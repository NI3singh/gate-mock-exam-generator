"""
Service to load syllabus and PYQ JSON files into PostgreSQL.

• Syllabus: reads from backend/data/syllabus/ (required files)
• PYQs:     reads from backend/data/pyqs/ (optional; produced by
            backend/scripts/ingest_pyq_pdf.py and reviewed by hand)
• Both are idempotent — existing rows for the same paper (or paper+year for
  PYQs) are deleted before inserting
• No embeddings (deferred — pyq_questions.embedding stays NULL)
"""

import json
from pathlib import Path

from sqlalchemy import delete, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.syllabus import Syllabus
from app.models.source_document import SourceDocument
from app.models.pyq_question import PYQuestion

# Resolve the data directory relative to this file
# services/data_loader.py  →  app/services/  →  app/  →  backend/
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
SYLLABUS_DIR = DATA_DIR / "syllabus"
PYQ_DIR = DATA_DIR / "pyqs"

VALID_PYQ_PAPERS = {"CS", "DA"}
VALID_PYQ_TYPES = {"MCQ", "MSQ", "NAT"}

EXPECTED_FILES = {
    "DA": "DA_syllabus.json",
    "CS": "CS_syllabus.json",
    "GA": "GA_syllabus.json",
}


class DataLoadResult:
    """Simple container for load results."""

    def __init__(self) -> None:
        self.papers_loaded: list[str] = []
        self.total_rows_inserted: int = 0
        self.details: dict[str, dict] = {}
        self.errors: list[str] = []

    def to_dict(self) -> dict:
        return {
            "papers_loaded": self.papers_loaded,
            "total_rows_inserted": self.total_rows_inserted,
            "details": self.details,
            "errors": self.errors,
        }


def _read_syllabus_json(filepath: Path) -> dict:
    """Read and parse a single syllabus JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Basic validation
    if "paper" not in data:
        raise ValueError(f"Missing 'paper' key in {filepath.name}")
    if "sections" not in data or not isinstance(data["sections"], list):
        raise ValueError(f"Missing or invalid 'sections' in {filepath.name}")

    return data


async def load_syllabus(db: AsyncSession) -> DataLoadResult:
    """
    Load ALL syllabus JSON files into the database.

    Steps per file:
      1. Parse JSON
      2. DELETE existing rows for that paper (idempotent)
      3. INSERT one row per topic
    """
    result = DataLoadResult()

    if not SYLLABUS_DIR.exists():
        result.errors.append(
            f"Syllabus directory not found: {SYLLABUS_DIR}. "
            "Create it and place DA_syllabus.json, CS_syllabus.json, GA_syllabus.json inside."
        )
        return result

    for paper_code, filename in EXPECTED_FILES.items():
        filepath = SYLLABUS_DIR / filename

        if not filepath.exists():
            result.errors.append(f"File not found: {filepath}")
            continue

        try:
            data = _read_syllabus_json(filepath)
        except (json.JSONDecodeError, ValueError) as exc:
            result.errors.append(f"Failed to parse {filename}: {exc}")
            continue

        paper = data["paper"]
        sections = data["sections"]

        # ── Step 1: Delete existing rows for this paper ──
        await db.execute(delete(Syllabus).where(Syllabus.paper == paper))

        # ── Step 2: Insert new rows ──
        rows_inserted = 0
        sections_count = 0

        for section in sections:
            section_name = section.get("section_name", "Unknown")
            topics = section.get("topics", [])
            sections_count += 1

            for topic in topics:
                row = Syllabus(
                    paper=paper,
                    section_name=section_name,
                    topic=topic,
                    subtopic=None,
                    source_file=filename,
                )
                db.add(row)
                rows_inserted += 1

        await db.flush()  # Flush so IDs are generated (but don't commit yet)

        result.papers_loaded.append(paper)
        result.total_rows_inserted += rows_inserted
        result.details[paper] = {
            "filename": filename,
            "sections": sections_count,
            "topics_inserted": rows_inserted,
        }

    # ── Commit all at once ──
    await db.commit()
    return result


def _read_pyq_json(filepath: Path) -> dict:
    """Read and validate the file-level structure of one PYQ JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("paper") not in VALID_PYQ_PAPERS:
        raise ValueError(
            f"'paper' must be one of {sorted(VALID_PYQ_PAPERS)} in {filepath.name}"
        )
    if not isinstance(data.get("year"), int):
        raise ValueError(f"'year' must be an integer in {filepath.name}")
    if not isinstance(data.get("questions"), list) or not data["questions"]:
        raise ValueError(f"'questions' must be a non-empty list in {filepath.name}")
    return data


def _validate_pyq_question(q: dict) -> list[str]:
    """Light row-level validation. Returns error strings; [] means valid."""
    errors: list[str] = []
    if not isinstance(q.get("qno"), int):
        errors.append("qno must be an integer")
    if q.get("question_type") not in VALID_PYQ_TYPES:
        errors.append(f"question_type must be one of {sorted(VALID_PYQ_TYPES)}")
    if q.get("marks") not in (1, 2):
        errors.append("marks must be 1 or 2")
    stem = q.get("stem")
    if not isinstance(stem, str) or not stem.strip():
        errors.append("stem must be a non-empty string")
    if q.get("question_type") in ("MCQ", "MSQ"):
        options = q.get("options")
        if not isinstance(options, (list, dict)) or len(options) != 4:
            errors.append("MCQ/MSQ questions need exactly 4 options")
    answer = q.get("answer")
    if answer is not None and (not isinstance(answer, str) or len(answer) > 50):
        errors.append("answer must be a string of at most 50 characters")
    return errors


async def load_pyqs(db: AsyncSession) -> DataLoadResult:
    """
    Load ALL PYQ JSON files from backend/data/pyqs/ into the database.

    PYQs are optional: a missing directory or no files is NOT an error, the
    result simply comes back empty. Per file:
      1. Parse + validate structure
      2. DELETE existing PYQ rows + source document for that (paper, year)
      3. INSERT a fresh SourceDocument and one PYQuestion per valid question
         (invalid questions are skipped and reported, never abort the file)
    """
    result = DataLoadResult()

    if not PYQ_DIR.exists():
        return result

    for filepath in sorted(PYQ_DIR.glob("*.json")):
        try:
            data = _read_pyq_json(filepath)
        except (json.JSONDecodeError, ValueError) as exc:
            result.errors.append(f"Failed to parse {filepath.name}: {exc}")
            continue

        paper = data["paper"]
        year = data["year"]

        # ── Step 1: Idempotent delete for this (paper, year) ──
        old_docs_result = await db.execute(
            select(SourceDocument.id).where(
                SourceDocument.paper == paper,
                SourceDocument.year == year,
                SourceDocument.doc_type == "PYQ",
            )
        )
        old_doc_ids = [row[0] for row in old_docs_result.fetchall()]
        if old_doc_ids:
            await db.execute(
                delete(PYQuestion).where(
                    PYQuestion.source_document_id.in_(old_doc_ids)
                )
            )
            await db.execute(
                delete(SourceDocument).where(SourceDocument.id.in_(old_doc_ids))
            )

        # ── Step 2: Insert source document + questions ──
        doc = SourceDocument(
            paper=paper,
            year=year,
            filename=data.get("source_filename", filepath.name),
            doc_type="PYQ",
            total_questions=0,
        )
        db.add(doc)
        await db.flush()  # need doc.id for the FK

        inserted = 0
        skipped = 0
        for q in data["questions"]:
            q_errors = _validate_pyq_question(q)
            if q_errors:
                skipped += 1
                result.errors.append(
                    f"{filepath.name} q{q.get('qno')}: {'; '.join(q_errors)}"
                )
                continue
            tolerance = q.get("tolerance")
            db.add(
                PYQuestion(
                    source_document_id=doc.id,
                    paper=paper,
                    year=year,
                    qno=q["qno"],
                    question_type=q["question_type"],
                    marks=q["marks"],
                    section_name=q.get("section_name"),
                    topic=q.get("topic") or "Unknown",
                    stem=q["stem"],
                    code_snippet=q.get("code_snippet"),
                    options=q.get("options"),
                    answer=q.get("answer"),
                    answer_value=q.get("answer_value"),
                    tolerance=tolerance if tolerance is not None else 0.01,
                    solution=q.get("solution"),
                    embedding=None,
                )
            )
            inserted += 1

        doc.total_questions = inserted
        await db.flush()

        label = f"PYQ {paper} {year}"
        result.papers_loaded.append(label)
        result.total_rows_inserted += inserted
        result.details[label] = {
            "filename": filepath.name,
            "questions_inserted": inserted,
            "questions_skipped": skipped,
        }

    # ── Commit all at once ──
    await db.commit()
    return result


async def get_pyq_stats(db: AsyncSession) -> dict:
    """Quick stats about what's currently loaded in the pyq_questions table."""
    stats: dict[str, dict] = {}

    for paper_code in sorted(VALID_PYQ_PAPERS):
        count_result = await db.execute(
            select(func.count(PYQuestion.id)).where(
                PYQuestion.paper == paper_code
            )
        )
        count = count_result.scalar() or 0

        years_result = await db.execute(
            select(PYQuestion.year)
            .where(PYQuestion.paper == paper_code)
            .distinct()
            .order_by(PYQuestion.year)
        )
        years = [row[0] for row in years_result.fetchall()]

        stats[paper_code] = {
            "total_questions": count,
            "years": years,
        }

    return stats


async def get_syllabus_stats(db: AsyncSession) -> dict:
    """Quick stats about what's currently loaded in the syllabus table."""
    stats: dict[str, dict] = {}

    for paper_code in ["CS", "DA", "GA"]:
        count_result = await db.execute(
            select(func.count(Syllabus.id)).where(Syllabus.paper == paper_code)
        )
        count = count_result.scalar() or 0

        section_result = await db.execute(
            select(Syllabus.section_name)
            .where(Syllabus.paper == paper_code)
            .distinct()
        )
        sections = [row[0] for row in section_result.fetchall()]

        stats[paper_code] = {
            "total_topics": count,
            "sections": sections,
            "section_count": len(sections),
        }

    return stats