"""Alter syllabus section_name, topic, subtopic, source_file to TEXT

Revision ID: 003
Revises: 002
Create Date: 2026-03-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE syllabus "
        "ALTER COLUMN section_name TYPE TEXT, "
        "ALTER COLUMN topic TYPE TEXT, "
        "ALTER COLUMN subtopic TYPE TEXT, "
        "ALTER COLUMN source_file TYPE TEXT"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE syllabus "
        "ALTER COLUMN section_name TYPE VARCHAR(255), "
        "ALTER COLUMN topic TYPE VARCHAR(255), "
        "ALTER COLUMN subtopic TYPE VARCHAR(255), "
        "ALTER COLUMN source_file TYPE VARCHAR(255)"
    )
