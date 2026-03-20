"""
Service to load syllabus JSON files into the PostgreSQL syllabus table.

• Reads from  backend/data/syllabus/
• Idempotent — deletes existing rows for the paper before inserting
• No PYQ loading, no embeddings (deferred to v2)
"""

import json
from pathlib import Path

from sqlalchemy import delete, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.syllabus import Syllabus

# Resolve the data directory relative to this file
# services/data_loader.py  →  app/services/  →  app/  →  backend/
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
SYLLABUS_DIR = DATA_DIR / "syllabus"

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