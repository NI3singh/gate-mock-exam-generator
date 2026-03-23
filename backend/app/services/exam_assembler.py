"""
Assembles a final 65-question exam from the pool of generated questions,
following the official GATE 2026 distribution rules.
"""

import logging
import random
from typing import Any

from app.core.llm_config import (
    GA_1MARK,
    GA_2MARK,
    GA_QUESTIONS,
    SUBJECT_1MARK,
    SUBJECT_2MARK,
    SUBJECT_QUESTIONS,
    GATE_TOTAL_QUESTIONS,
)

logger = logging.getLogger(__name__)


def assemble_exam(
    generated_questions: list[dict],
    paper: str,
) -> tuple[list[dict], list[dict]]:
    """
    Select and order exactly 65 questions from the generated pool.

    Returns:
        (question_order, selected_questions)

        question_order: list of dicts with keys:
            qno, question_id, marks, type, section

        selected_questions: the actual question dicts (to store IDs)
    """
    # ── Separate GA and Subject questions ──
    ga_pool = [q for q in generated_questions if q.get("section_name") == "General Aptitude"]
    subj_pool = [q for q in generated_questions if q.get("section_name") != "General Aptitude"]

    logger.info(f"Assembly pool: {len(ga_pool)} GA, {len(subj_pool)} Subject")

    # ── Select GA questions ──
    ga_1m = _select_n(ga_pool, n=GA_1MARK, marks=1)
    ga_2m = _select_n(ga_pool, n=GA_2MARK, marks=2)
    ga_selected = ga_1m + ga_2m

    # ── Select Subject questions ──
    subj_1m = _select_n(subj_pool, n=SUBJECT_1MARK, marks=1)
    subj_2m = _select_n(subj_pool, n=SUBJECT_2MARK, marks=2)
    subj_selected = subj_1m + subj_2m

    # ── Combine ──
    all_selected = ga_selected + subj_selected

    logger.info(
        f"Assembled: {len(ga_selected)} GA + {len(subj_selected)} Subject "
        f"= {len(all_selected)} total"
    )

    # ── Verify counts ──
    if len(all_selected) < GATE_TOTAL_QUESTIONS:
        logger.warning(
            f"Only assembled {len(all_selected)}/{GATE_TOTAL_QUESTIONS} questions. "
            f"Exam will be shorter than standard."
        )

    # ── Build question_order ──
    question_order = []
    for i, q in enumerate(all_selected):
        question_order.append({
            "qno": i + 1,
            "question_id": q.get("_id", ""),  # Will be replaced with actual UUID after storage
            "marks": q["marks"],
            "type": q["question_type"],
            "section": "GA" if q.get("section_name") == "General Aptitude" else "Subject",
            "section_name": q["section_name"],
            "topic": q["topic"],
        })

    return question_order, all_selected


def _select_n(
    pool: list[dict],
    n: int,
    marks: int,
) -> list[dict]:
    """
    Select n questions with the given marks value from pool.
    Tries to maximise topic diversity.
    """
    # Filter by marks
    candidates = [q for q in pool if q.get("marks") == marks]

    if len(candidates) <= n:
        return candidates

    # ── Diversify by topic ──
    selected: list[dict] = []
    used_topics: set[str] = set()

    # First pass: one per topic
    shuffled = candidates[:]
    random.shuffle(shuffled)

    for q in shuffled:
        topic = q.get("topic", "")
        if topic not in used_topics and len(selected) < n:
            selected.append(q)
            used_topics.add(topic)

    # Second pass: fill remaining from unused candidates
    if len(selected) < n:
        remaining = [q for q in shuffled if q not in selected]
        for q in remaining:
            if len(selected) >= n:
                break
            selected.append(q)

    return selected[:n]


def compute_marks_summary(question_order: list[dict]) -> dict:
    """Compute marks breakdown for verification."""
    ga_marks = sum(q["marks"] for q in question_order if q["section"] == "GA")
    subj_marks = sum(q["marks"] for q in question_order if q["section"] == "Subject")
    total_marks = ga_marks + subj_marks

    type_counts = {}
    for q in question_order:
        t = q["type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    return {
        "total_questions": len(question_order),
        "total_marks": total_marks,
        "ga_questions": sum(1 for q in question_order if q["section"] == "GA"),
        "ga_marks": ga_marks,
        "subject_questions": sum(1 for q in question_order if q["section"] == "Subject"),
        "subject_marks": subj_marks,
        "type_counts": type_counts,
    }