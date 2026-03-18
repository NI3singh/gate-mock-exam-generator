from sqlalchemy import String, Integer, Float, JSON, ForeignKey, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from pgvector.sqlalchemy import Vector  # Requires `pip install pgvector`


class PYQuestion(Base):
    __tablename__ = "pyq_questions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_document_id: Mapped[int] = mapped_column(
        ForeignKey("source_documents.id"), nullable=False
    )
    paper: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    qno: Mapped[int] = mapped_column(Integer, nullable=False)
    question_type: Mapped[str] = mapped_column(String(10), nullable=False)  # 'MCQ', 'MSQ', 'NAT'
    marks: Mapped[int] = mapped_column(Integer)  # 1 or 2
    section_name: Mapped[str | None] = mapped_column(String(255))
    topic: Mapped[str] = mapped_column(String(255), index=True)
    stem: Mapped[str] = mapped_column(String, nullable=False)
    code_snippet: Mapped[str | None] = mapped_column(String)
    options: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    answer: Mapped[str | None] = mapped_column(String(50))
    answer_value: Mapped[float | None] = mapped_column(Float)
    tolerance: Mapped[float] = mapped_column(Float, default=0.01)
    solution: Mapped[str | None] = mapped_column(String)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(384))  # pgvector
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )