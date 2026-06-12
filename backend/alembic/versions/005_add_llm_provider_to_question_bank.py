"""Add LLM provider metadata to question bank

Revision ID: 005
Revises: 004
Create Date: 2026-05-19
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "question_bank",
        sa.Column("llm_provider", sa.String(length=50), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("question_bank", "llm_provider")
