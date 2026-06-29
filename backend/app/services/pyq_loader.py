"""
Load structured PYQ JSON files (data/pyq/json/*.json) into the database.

For each file: upsert one `source_documents` row and its `pyq_questions` rows
(idempotent per paper+year), computing a 384-dim embedding per question for
similarity retrieval. If embeddings are unavailable the rows are still loaded
(embedding = NULL) and a warning is logged.
"""

import json
import logging
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pyq_question import PYQuestion
from app.models.source_document import SourceDocument
from app.services.embedding_service import embed_texts, embeddings_available

logger = logging.getLogger(__name__)

PYQ_JSON_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "pyq" / "json"

_REQUIRED_KEYS = {"paper", "year", "questions"}


def _embed_text_for(q: dict) -> str:
    """The text we embed for retrieval: section + topic + stem (concept-focused)."""
    parts = [q.get("section_name") or "", q.get("topic") or "", q.get("stem") or ""]
    return ". ".join(p for p in parts if p)


async def _load_one_file(db: AsyncSession, path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    missing = _REQUIRED_KEYS - set(data)
    if missing:
        raise ValueError(f"missing keys {missing}")

    paper = data["paper"]
    year = int(data["year"])
    doc_type = data.get("doc_type", "PYQ")
    questions = data.get("questions", [])

    # Idempotent: clear existing rows for this (paper, year) before re-inserting.
    await db.execute(
        delete(PYQuestion).where(PYQuestion.paper == paper, PYQuestion.year == year)
    )
    await db.execute(
        delete(SourceDocument).where(
            SourceDocument.paper == paper, SourceDocument.year == year
        )
    )

    src = SourceDocument(
        paper=paper,
        year=year,
        filename=path.name,
        doc_type=doc_type,
        total_questions=len(questions),
    )
    db.add(src)
    await db.flush()  # populate src.id

    vectors = None
    if questions and embeddings_available():
        vectors = embed_texts([_embed_text_for(q) for q in questions])

    for i, q in enumerate(questions):
        tolerance = q.get("tolerance")
        db.add(
            PYQuestion(
                source_document_id=src.id,
                paper=paper,
                year=year,
                qno=int(q.get("qno", i + 1)),
                question_type=q["question_type"],
                marks=int(q.get("marks", 1)),
                section_name=q.get("section_name"),
                topic=q.get("topic") or "General",
                stem=q["stem"],
                code_snippet=q.get("code_snippet"),
                options=q.get("options"),
                answer=q.get("answer"),
                answer_value=q.get("answer_value"),
                tolerance=tolerance if tolerance is not None else 0.01,
                solution=q.get("solution"),
                embedding=(vectors[i] if vectors is not None else None),
            )
        )

    return {
        "file": path.name,
        "paper": paper,
        "year": year,
        "questions": len(questions),
        "embedded": vectors is not None,
    }


async def load_pyq_files(db: AsyncSession, json_dir: Path | None = None) -> dict:
    """Load every data/pyq/json/*.json file into the database."""
    json_dir = json_dir or PYQ_JSON_DIR
    result: dict = {
        "files": [],
        "total_questions": 0,
        "errors": [],
        "embeddings_available": embeddings_available(),
    }

    if not json_dir.exists():
        result["errors"].append(f"PYQ json dir not found: {json_dir}")
        return result

    files = sorted(json_dir.glob("*.json"))
    if not files:
        result["errors"].append(f"No PYQ json files in {json_dir}")
        return result

    for path in files:
        try:
            info = await _load_one_file(db, path)
            result["files"].append(info)
            result["total_questions"] += info["questions"]
            logger.info("Loaded %s: %s questions", path.name, info["questions"])
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to load PYQ file %s", path.name)
            result["errors"].append(f"{path.name}: {exc}")

    await db.commit()
    return result
