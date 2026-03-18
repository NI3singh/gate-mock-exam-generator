import uuid

from sqlalchemy import String, Integer, JSON, ForeignKey, Float, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserAnalytics(Base):
    __tablename__ = "user_analytics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    paper: Mapped[str | None] = mapped_column(String(10), nullable=True)
    total_exams_taken: Mapped[int] = mapped_column(Integer, default=0)
    average_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    best_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    worst_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    topic_proficiency: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    score_history: Mapped[list | None] = mapped_column(JSON, nullable=True)
    weak_topics: Mapped[list | None] = mapped_column(JSON, nullable=True)
    strong_topics: Mapped[list | None] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )