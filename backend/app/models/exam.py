import uuid

from sqlalchemy import String, Integer, JSON, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func

from app.core.database import Base


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    paper: Mapped[str] = mapped_column(String(10), nullable=False)
    scope: Mapped[str] = mapped_column(String(20), nullable=False)
    selected_topics: Mapped[list | None] = mapped_column(JSON, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(10), nullable=False)
    use_pyq_reference: Mapped[bool] = mapped_column(Boolean, default=True)
    types_ratio: Mapped[dict] = mapped_column(
        JSON, default={"MCQ": 0.6, "MSQ": 0.2, "NAT": 0.2}
    )
    total_questions: Mapped[int] = mapped_column(Integer, default=65)
    total_marks: Mapped[int] = mapped_column(Integer, default=100)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=180)
    question_ids: Mapped[list] = mapped_column(JSON, nullable=False)
    question_order: Mapped[list] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="generated")
    generation_progress: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )