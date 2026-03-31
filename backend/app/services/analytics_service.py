from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Any
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attempt import Attempt
from app.models.exam import Exam
from app.models.user_analytics import UserAnalytics
from app.schemas.analytics import (
    AnalyticsDashboardResponse,
    ScoreHistoryPoint,
    TopicPerformanceItem,
    TopicPerformanceResponse,
)
from app.schemas.dashboard import DashboardStats, RecentExam

logger = logging.getLogger(__name__)


def _safe_percentage(score: float, max_score: float) -> float:
    if max_score <= 0:
        return 0.0
    return round((score / max_score) * 100, 2)


def _serialize_score_history(
    items: list[dict[str, Any]],
) -> list[ScoreHistoryPoint]:
    return [ScoreHistoryPoint(**item) for item in items]


def _serialize_topic_items(
    items: list[dict[str, Any]],
) -> list[TopicPerformanceItem]:
    return [TopicPerformanceItem(**item) for item in items]


async def _fetch_completed_attempt_rows(
    db: AsyncSession,
    user_id: UUID | str,
) -> list[tuple[Attempt, Exam]]:
    result = await db.execute(
        select(Attempt, Exam)
        .join(Exam, Exam.id == Attempt.exam_id)
        .where(
            Attempt.user_id == user_id,
            Attempt.submitted.is_(True),
        )
        .order_by(Attempt.created_at.asc())
    )
    return [(attempt, exam) for attempt, exam in result.all()]


def _build_analytics_snapshot(
    rows: list[tuple[Attempt, Exam]],
) -> dict[str, Any]:
    if not rows:
        return {
            "paper": None,
            "total_exams_taken": 0,
            "average_score": None,
            "best_score": None,
            "worst_score": None,
            "total_questions_attempted": 0,
            "improvement_percentage": 0.0,
            "score_history": [],
            "topic_items": [],
            "weak_topics": [],
            "strong_topics": [],
            "topic_proficiency": {},
        }

    scores: list[float] = []
    score_history: list[dict[str, Any]] = []
    topic_map: dict[tuple[str, str], dict[str, Any]] = {}
    total_questions_attempted = 0

    for index, (attempt, exam) in enumerate(rows, start=1):
        score = round(float(attempt.score or 0.0), 2)
        max_score = float(attempt.max_score or exam.total_marks or 100)
        percentage = _safe_percentage(score, max_score)
        scores.append(score)

        taken_at = attempt.end_time or attempt.created_at or exam.created_at
        if isinstance(taken_at, str):
            taken_at = datetime.fromisoformat(taken_at)

        total_questions_attempted += (attempt.total_correct or 0) + (attempt.total_wrong or 0)

        score_history.append(
            {
                "attempt_id": str(attempt.id),
                "exam_id": str(exam.id),
                "paper": exam.paper,
                "score": score,
                "max_score": max_score,
                "percentage": percentage,
                "submitted_at": taken_at.isoformat(),
                "label": f"Exam {index}",
            }
        )

        for item in attempt.topic_analysis or []:
            topic = str(item.get("topic", "Unknown"))
            section_name = str(item.get("section_name", "Subject"))
            key = (section_name, topic)

            if key not in topic_map:
                topic_map[key] = {
                    "topic": topic,
                    "section_name": section_name,
                    "total_questions": 0,
                    "correct": 0,
                    "wrong": 0,
                    "unanswered": 0,
                    "score": 0.0,
                    "max_score": 0.0,
                    "accuracy": 0.0,
                    "attempts_covered": 0,
                }

            agg = topic_map[key]
            agg["total_questions"] += int(item.get("total", 0) or 0)
            agg["correct"] += int(item.get("correct", 0) or 0)
            agg["wrong"] += int(item.get("wrong", 0) or 0)
            agg["unanswered"] += int(item.get("unanswered", 0) or 0)
            agg["score"] += float(item.get("score", 0.0) or 0.0)
            agg["max_score"] += float(item.get("max_score", 0.0) or 0.0)
            agg["attempts_covered"] += 1

    topic_items = list(topic_map.values())
    for item in topic_items:
        item["score"] = round(item["score"], 2)
        item["max_score"] = round(item["max_score"], 2)
        item["accuracy"] = (
            round((item["correct"] / item["total_questions"]) * 100, 2)
            if item["total_questions"] > 0
            else 0.0
        )

    strong_topics = sorted(
        topic_items,
        key=lambda item: (-item["accuracy"], -item["total_questions"], item["topic"].lower()),
    )[:5]
    weak_topics = sorted(
        topic_items,
        key=lambda item: (item["accuracy"], -item["total_questions"], item["topic"].lower()),
    )[:5]

    topic_proficiency = {
        f"{item['section_name']}::{item['topic']}": item
        for item in topic_items
    }

    first_percentage = score_history[0]["percentage"]
    last_percentage = score_history[-1]["percentage"]
    improvement_percentage = round(last_percentage - first_percentage, 2)

    return {
        "paper": rows[-1][1].paper,
        "total_exams_taken": len(rows),
        "average_score": round(sum(scores) / len(scores), 2),
        "best_score": round(max(scores), 2),
        "worst_score": round(min(scores), 2),
        "total_questions_attempted": total_questions_attempted,
        "improvement_percentage": improvement_percentage,
        "score_history": score_history,
        "topic_items": topic_items,
        "weak_topics": weak_topics,
        "strong_topics": strong_topics,
        "topic_proficiency": topic_proficiency,
    }


async def recompute_user_analytics(
    db: AsyncSession,
    user_id: UUID | str,
) -> dict[str, Any]:
    rows = await _fetch_completed_attempt_rows(db, user_id)
    snapshot = _build_analytics_snapshot(rows)

    analytics_result = await db.execute(
        select(UserAnalytics).where(
            UserAnalytics.user_id == user_id,
            UserAnalytics.paper.is_(None),
        )
    )
    analytics = analytics_result.scalars().first()

    if analytics is None:
        analytics = UserAnalytics(
            user_id=user_id,
            paper=None,
        )
        db.add(analytics)

    analytics.paper = snapshot["paper"]
    analytics.total_exams_taken = snapshot["total_exams_taken"]
    analytics.average_score = snapshot["average_score"]
    analytics.best_score = snapshot["best_score"]
    analytics.worst_score = snapshot["worst_score"]
    analytics.topic_proficiency = snapshot["topic_proficiency"]
    analytics.score_history = snapshot["score_history"]
    analytics.weak_topics = snapshot["weak_topics"]
    analytics.strong_topics = snapshot["strong_topics"]
    analytics.updated_at = datetime.now(timezone.utc)

    await db.commit()
    return snapshot


async def get_dashboard_summary(
    db: AsyncSession,
    user_id: UUID | str,
) -> DashboardStats:
    snapshot = await recompute_user_analytics(db, user_id)

    recent_result = await db.execute(
        select(Exam, Attempt)
        .outerjoin(
            Attempt,
            and_(
                Attempt.exam_id == Exam.id,
                Attempt.user_id == user_id,
            ),
        )
        .where(Exam.user_id == user_id)
        .order_by(Exam.created_at.desc())
        .limit(8)
    )

    recent_exams: list[RecentExam] = []
    seen_exam_ids: set[str] = set()
    for exam, attempt in recent_result.all():
        exam_id = str(exam.id)
        if exam_id in seen_exam_ids:
            continue
        seen_exam_ids.add(exam_id)

        recent_exams.append(
            RecentExam(
                id=exam.id,
                paper=exam.paper,
                scope=exam.scope,
                difficulty=exam.difficulty,
                total_questions=exam.total_questions,
                total_marks=exam.total_marks,
                status=exam.status,
                score=round(float(attempt.score), 2) if attempt and attempt.score is not None else None,
                max_score=attempt.max_score if attempt and attempt.max_score is not None else exam.total_marks,
                created_at=exam.created_at,
            )
        )

    return DashboardStats(
        total_exams_taken=snapshot["total_exams_taken"],
        average_score=snapshot["average_score"],
        best_score=snapshot["best_score"],
        worst_score=snapshot["worst_score"],
        total_questions_attempted=snapshot["total_questions_attempted"],
        recent_exams=recent_exams,
    )


async def get_analytics_dashboard(
    db: AsyncSession,
    user_id: UUID | str,
) -> AnalyticsDashboardResponse:
    snapshot = await recompute_user_analytics(db, user_id)

    return AnalyticsDashboardResponse(
        total_exams_taken=snapshot["total_exams_taken"],
        average_score=snapshot["average_score"],
        best_score=snapshot["best_score"],
        worst_score=snapshot["worst_score"],
        total_questions_attempted=snapshot["total_questions_attempted"],
        improvement_percentage=snapshot["improvement_percentage"],
        score_history=_serialize_score_history(snapshot["score_history"]),
        weak_topics=_serialize_topic_items(snapshot["weak_topics"]),
        strong_topics=_serialize_topic_items(snapshot["strong_topics"]),
    )


async def get_topic_performance(
    db: AsyncSession,
    user_id: UUID | str,
) -> TopicPerformanceResponse:
    snapshot = await recompute_user_analytics(db, user_id)
    topics = sorted(
        snapshot["topic_items"],
        key=lambda item: (-item["total_questions"], item["topic"].lower()),
    )
    return TopicPerformanceResponse(topics=_serialize_topic_items(topics))


async def refresh_user_analytics_safely(
    db: AsyncSession,
    user_id: UUID | str,
) -> None:
    try:
        await recompute_user_analytics(db, user_id)
    except Exception:
        logger.exception("Failed to refresh analytics for user %s", user_id)
