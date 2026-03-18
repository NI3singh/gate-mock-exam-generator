import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    firebase_uid: Mapped[str] = mapped_column(
        String(128), unique=True, nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    preferred_paper: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "preferred_paper IN ('CS', 'DA') OR preferred_paper IS NULL",
            name="check_preferred_paper",
        ),
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"