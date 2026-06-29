"""
Retrieve previous-year questions (PYQs) as grounding exemplars for generation.

Given a batch's (paper, section, topics), find the most semantically similar real
questions via pgvector cosine search and render them as a reference block to
prepend to the generation prompt. General Aptitude is pooled across all papers;
subject questions are filtered to the exam's paper.

Never raises to the caller: if grounding is disabled, embeddings are unavailable,
or no PYQs are loaded, it returns an empty result and generation proceeds
ungrounded (its previous behaviour).
"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.pyq_question import PYQuestion
from app.services.embedding_service import embed_text

logger = logging.getLogger(__name__)

GA_SECTION = "General Aptitude"
_LETTERS = ["A", "B", "C", "D", "E", "F"]


async def retrieve_exemplars(
    db: AsyncSession,
    *,
    paper: str,
    section_name: str,
    topics: list[str],
    k: int | None = None,
) -> list[PYQuestion]:
    """Return up to k PYQ rows most similar to (section_name, topics)."""
    if not settings.PYQ_GROUNDING_ENABLED:
        return []

    k = k or settings.PYQ_RETRIEVAL_TOP_K
    query_text = ". ".join([section_name] + list(topics[:6]))
    qvec = embed_text(query_text)
    if qvec is None:
        return []

    stmt = select(PYQuestion).where(PYQuestion.embedding.isnot(None))
    if section_name == GA_SECTION:
        stmt = stmt.where(PYQuestion.section_name == GA_SECTION)
    else:
        stmt = stmt.where(PYQuestion.paper == paper)
    stmt = stmt.order_by(PYQuestion.embedding.cosine_distance(qvec)).limit(k)

    try:
        rows = (await db.execute(stmt)).scalars().all()
    except Exception as exc:  # noqa: BLE001
        logger.warning("PYQ retrieval query failed (continuing ungrounded): %s", exc)
        return []
    return list(rows)


def format_exemplars(rows: list[PYQuestion]) -> str:
    """Render retrieved PYQs as a reference block to prepend to the prompt."""
    if not rows:
        return ""

    lines = [
        "REFERENCE — authentic previous-year GATE questions, for calibration only.",
        "Match their depth, style, and difficulty. Generate NEW questions on the "
        "requested topics; do NOT copy, paraphrase, or reuse these:",
        "",
    ]
    for i, q in enumerate(rows, 1):
        marks = f"{q.marks} mark" + ("s" if (q.marks or 0) != 1 else "")
        lines.append(f"[{i}] ({q.question_type}, {marks}) {q.stem}")
        if isinstance(q.options, list):
            opts = "   ".join(
                f"{_LETTERS[j]}) {opt}"
                for j, opt in enumerate(q.options)
                if j < len(_LETTERS)
            )
            lines.append(f"    {opts}")
        if q.answer:
            lines.append(f"    Answer: {q.answer}")
        elif q.answer_value is not None:
            lines.append(f"    Answer: {q.answer_value}")
        lines.append("")

    return "\n".join(lines).strip()
