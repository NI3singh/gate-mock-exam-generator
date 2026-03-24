import uuid
from datetime import datetime

from sqlalchemy import String, Float, Integer, JSON, ForeignKey, Boolean, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    exam_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    start_time: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    end_time: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    submitted: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_submitted: Mapped[bool] = mapped_column(Boolean, default=False)
    responses: Mapped[dict] = mapped_column(JSON, default=dict)
    question_statuses: Mapped[dict] = mapped_column(JSON, default=dict)
    events_log: Mapped[list] = mapped_column(JSON, default=list)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_score: Mapped[int] = mapped_column(Integer, default=100)
    total_correct: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_wrong: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_unanswered: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_breakdown: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    topic_analysis: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )