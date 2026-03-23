"""Add 'failed' to exam status check constraint

Revision ID: 004
Revises: 003
Create Date: 2026-03-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE exams DROP CONSTRAINT IF EXISTS check_exam_status"
    )
    op.execute(
        "ALTER TABLE exams ADD CONSTRAINT check_exam_status "
        "CHECK (status IN ('generating', 'generated', 'in_progress', 'completed', 'expired', 'failed'))"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE exams DROP CONSTRAINT IF EXISTS check_exam_status"
    )
    op.execute(
        "ALTER TABLE exams ADD CONSTRAINT check_exam_status "
        "CHECK (status IN ('generating', 'generated', 'in_progress', 'completed', 'expired'))"
    )
