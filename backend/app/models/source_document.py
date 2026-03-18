from sqlalchemy import Integer, String, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SourceDocument(Base):
    __tablename__ = "source_documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    paper: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(20), nullable=False)
    total_questions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    loaded_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )