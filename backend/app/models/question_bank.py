import uuid
from sqlalchemy import String, Integer, Float, JSON, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from pgvector.sqlalchemy import Vector


class QuestionBank(Base):
    __tablename__ = "question_bank"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    paper: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    question_type: Mapped[str] = mapped_column(String(10), nullable=False)  # 'MCQ', 'MSQ', 'NAT'
    marks: Mapped[int] = mapped_column(Integer)  # 1 or 2
    difficulty: Mapped[str] = mapped_column(String(10), nullable=False)  # 'easy', 'medium', 'hard'
    difficulty_score: Mapped[float] = mapped_column(Float)
    section_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    topic: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    stem_tex: Mapped[str] = mapped_column(String, nullable=False)
    code_snippet: Mapped[str | None] = mapped_column(String)
    code_language: Mapped[str | None] = mapped_column(String(20))
    choices: Mapped[list | None] = mapped_column(JSON, nullable=True)
    answer: Mapped[dict] = mapped_column(JSON, nullable=False)
    solution_tex: Mapped[str] = mapped_column(String, nullable=False)
    estimated_time_seconds: Mapped[int | None] = mapped_column(Integer)
    provenance: Mapped[list | None] = mapped_column(JSON, nullable=True)
    llm_model: Mapped[str | None] = mapped_column(String(100))
    llm_prompt_version: Mapped[str | None] = mapped_column(String(50))
    validated: Mapped[bool] = mapped_column(default=False)
    validation_notes: Mapped[str | None] = mapped_column(String)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(384))  # pgvector
    generated_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )