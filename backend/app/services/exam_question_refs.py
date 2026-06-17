"""Resolve ordered question references for an exam (shared by API, grading, PDF)."""

from __future__ import annotations

import logging
from typing import Any

from app.models.exam import Exam

logger = logging.getLogger(__name__)

GA_SECTION_NAMES = frozenset({"ga", "general aptitude"})


def section_bucket(section_name: str | None, *, order_section: str | None = None) -> str:
    """Map DB / order metadata to GA vs Subject."""
    if order_section == "GA":
        return "GA"
    if (section_name or "").strip().lower() in GA_SECTION_NAMES:
        return "GA"
    if (order_section or "").strip().lower() in GA_SECTION_NAMES:
        return "GA"
    return "Subject"


def resolve_exam_question_refs(exam: Exam) -> list[dict[str, Any]]:
    """
    Return ordered question refs: qno, question_id, section, section_name.

    Merges ``question_order`` with ``question_ids`` by index so partially empty
    ``question_id`` fields (legacy or corrupt rows) still resolve.
    """
    order_raw: list[Any] = list(exam.question_order or [])
    fallback_ids = [str(qid).strip() for qid in (exam.question_ids or []) if qid]

    refs: list[dict[str, Any]] = []

    if order_raw:
        for idx, entry in enumerate(order_raw):
            qno = idx + 1
            question_id: str | None = None
            section = "Subject"
            section_name: str | None = None

            if isinstance(entry, dict):
                qno = int(entry.get("qno") or idx + 1)
                raw_id = entry.get("question_id")
                if raw_id:
                    question_id = str(raw_id).strip()
                section = entry.get("section") or section
                section_name = entry.get("section_name")
            elif entry:
                question_id = str(entry).strip()

            if not question_id and idx < len(fallback_ids):
                question_id = fallback_ids[idx]

            if question_id:
                refs.append(
                    {
                        "qno": qno,
                        "question_id": question_id,
                        "section": section,
                        "section_name": section_name,
                    }
                )
    elif fallback_ids:
        for idx, qid in enumerate(fallback_ids):
            refs.append(
                {
                    "qno": idx + 1,
                    "question_id": qid,
                    "section": "Subject",
                    "section_name": None,
                }
            )

    # Stable sort by qno; drop duplicate IDs (keep first occurrence).
    refs.sort(key=lambda r: int(r["qno"]))
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for ref in refs:
        qid = ref["question_id"]
        if qid in seen:
            logger.warning("Duplicate question_id %s in exam %s — skipping", qid, exam.id)
            continue
        seen.add(qid)
        unique.append(ref)

    return unique


def lookup_response(responses: dict[str, Any] | None, question_id: str) -> Any:
    """Find a user response; tolerate UUID key casing differences."""
    if not responses:
        return None

    qid = str(question_id).strip()
    if qid in responses:
        return responses[qid]

    lower = qid.lower()
    for key, value in responses.items():
        if str(key).strip().lower() == lower:
            return value

    return None
