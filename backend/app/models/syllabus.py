from sqlalchemy import Text, func, String
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Syllabus(Base):
    __tablename__ = "syllabus"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    paper: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    section_name: Mapped[str] = mapped_column(Text(), nullable=False, index=True)
    topic: Mapped[str] = mapped_column(Text(), nullable=False, index=True)
    subtopic: Mapped[str | None] = mapped_column(Text(), nullable=True)
    source_file: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )