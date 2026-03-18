"""create users table

Revision ID: 001
Revises:
Create Date: 2025-07-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("firebase_uid", sa.String(128), unique=True, nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("preferred_paper", sa.String(10), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "preferred_paper IN ('CS', 'DA') OR preferred_paper IS NULL",
            name="check_preferred_paper",
        ),
    )

    op.create_index("idx_users_firebase_uid", "users", ["firebase_uid"])


def downgrade() -> None:
    op.drop_index("idx_users_firebase_uid", table_name="users")
    op.drop_table("users")