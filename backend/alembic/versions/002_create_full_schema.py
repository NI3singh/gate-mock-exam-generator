"""Create full schema - all tables, pgvector, indexes

Revision ID: 002
Revises: 001
Create Date: 2025-07-15
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ──────────────────────────────────────
    # 1. Enable pgvector extension
    # ──────────────────────────────────────
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ──────────────────────────────────────
    # 2. syllabus table
    # ──────────────────────────────────────
    op.create_table(
        "syllabus",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("paper", sa.String(10), nullable=False),
        sa.Column("section_name", sa.String(255), nullable=False),
        sa.Column("topic", sa.String(255), nullable=False),
        sa.Column("subtopic", sa.String(255), nullable=True),
        sa.Column("source_file", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_syllabus_paper", "syllabus", ["paper"])
    op.create_index("ix_syllabus_section_name", "syllabus", ["section_name"])
    op.create_index("ix_syllabus_topic", "syllabus", ["topic"])

    # ──────────────────────────────────────
    # 3. source_documents table
    # ──────────────────────────────────────
    op.create_table(
        "source_documents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("paper", sa.String(10), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("doc_type", sa.String(20), nullable=False),
        sa.Column("total_questions", sa.Integer(), nullable=True),
        sa.Column(
            "loaded_at",
            TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "doc_type IN ('PYQ', 'SAMPLE', 'SYLLABUS')",
            name="check_doc_type",
        ),
    )
    op.create_index("ix_source_documents_paper", "source_documents", ["paper"])

    # ──────────────────────────────────────
    # 4. pyq_questions table
    # ──────────────────────────────────────
    op.create_table(
        "pyq_questions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "source_document_id",
            sa.Integer(),
            sa.ForeignKey("source_documents.id"),
            nullable=False,
        ),
        sa.Column("paper", sa.String(10), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("qno", sa.Integer(), nullable=False),
        sa.Column("question_type", sa.String(10), nullable=False),
        sa.Column("marks", sa.Integer(), nullable=False),
        sa.Column("section_name", sa.String(255), nullable=True),
        sa.Column("topic", sa.String(255), nullable=True),
        sa.Column("stem", sa.Text(), nullable=False),
        sa.Column("code_snippet", sa.Text(), nullable=True),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.Column("answer", sa.String(50), nullable=True),
        sa.Column("answer_value", sa.Double(), nullable=True),
        sa.Column("tolerance", sa.Double(), server_default="0.01"),
        sa.Column("solution", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "question_type IN ('MCQ', 'MSQ', 'NAT')",
            name="check_pyq_question_type",
        ),
        sa.CheckConstraint(
            "marks IN (1, 2)",
            name="check_pyq_marks",
        ),
    )
    # Add vector column separately (Alembic doesn't natively know the vector type)
    op.execute("ALTER TABLE pyq_questions ADD COLUMN embedding vector(384)")

    op.create_index("idx_pyq_paper_topic", "pyq_questions", ["paper", "topic"])
    op.create_index("ix_pyq_paper", "pyq_questions", ["paper"])
    op.create_index("ix_pyq_year", "pyq_questions", ["year"])
    op.create_index("ix_pyq_topic", "pyq_questions", ["topic"])

    # ──────────────────────────────────────
    # 5. question_bank table
    # ──────────────────────────────────────
    op.create_table(
        "question_bank",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("paper", sa.String(10), nullable=False),
        sa.Column("question_type", sa.String(10), nullable=False),
        sa.Column("marks", sa.Integer(), nullable=False),
        sa.Column("difficulty", sa.String(10), nullable=False),
        sa.Column("difficulty_score", sa.Double(), nullable=True),
        sa.Column("section_name", sa.String(255), nullable=False),
        sa.Column("topic", sa.String(255), nullable=False),
        sa.Column("stem_tex", sa.Text(), nullable=False),
        sa.Column("code_snippet", sa.Text(), nullable=True),
        sa.Column("code_language", sa.String(20), nullable=True),
        sa.Column("choices", sa.JSON(), nullable=True),
        sa.Column("answer", sa.JSON(), nullable=False),
        sa.Column("solution_tex", sa.Text(), nullable=False),
        sa.Column("estimated_time_seconds", sa.Integer(), nullable=True),
        sa.Column("provenance", sa.JSON(), nullable=True),
        sa.Column("llm_model", sa.String(100), nullable=True),
        sa.Column("llm_prompt_version", sa.String(50), nullable=True),
        sa.Column("validated", sa.Boolean(), server_default="false"),
        sa.Column("validation_notes", sa.Text(), nullable=True),
        sa.Column(
            "generated_at",
            TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "question_type IN ('MCQ', 'MSQ', 'NAT')",
            name="check_qb_question_type",
        ),
        sa.CheckConstraint(
            "marks IN (1, 2)",
            name="check_qb_marks",
        ),
        sa.CheckConstraint(
            "difficulty IN ('easy', 'medium', 'hard')",
            name="check_qb_difficulty",
        ),
        sa.CheckConstraint(
            "difficulty_score >= 0 AND difficulty_score <= 1",
            name="check_qb_difficulty_score",
        ),
    )
    # Add vector column separately
    op.execute("ALTER TABLE question_bank ADD COLUMN embedding vector(384)")

    op.create_index("idx_qbank_paper_topic", "question_bank", ["paper", "topic"])
    op.create_index("idx_qbank_difficulty", "question_bank", ["paper", "difficulty"])
    op.create_index("ix_qbank_paper", "question_bank", ["paper"])
    op.create_index("ix_qbank_section_name", "question_bank", ["section_name"])
    op.create_index("ix_qbank_topic", "question_bank", ["topic"])

    # ──────────────────────────────────────
    # 6. exams table
    # ──────────────────────────────────────
    op.create_table(
        "exams",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("paper", sa.String(10), nullable=False),
        sa.Column("scope", sa.String(20), nullable=False),
        sa.Column("selected_topics", sa.JSON(), nullable=True),
        sa.Column("difficulty", sa.String(10), nullable=False),
        sa.Column("use_pyq_reference", sa.Boolean(), server_default="true"),
        sa.Column(
            "types_ratio",
            sa.JSON(),
            server_default='{"MCQ": 0.6, "MSQ": 0.2, "NAT": 0.2}',
        ),
        sa.Column("total_questions", sa.Integer(), server_default="65"),
        sa.Column("total_marks", sa.Integer(), server_default="100"),
        sa.Column("duration_minutes", sa.Integer(), server_default="180"),
        sa.Column("question_ids", sa.JSON(), nullable=False),
        sa.Column("question_order", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(20), server_default="generated"),
        sa.Column("generation_progress", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "scope IN ('full', 'topic')",
            name="check_exam_scope",
        ),
        sa.CheckConstraint(
            "difficulty IN ('easy', 'medium', 'hard', 'auto')",
            name="check_exam_difficulty",
        ),
        sa.CheckConstraint(
            "status IN ('generating', 'generated', 'in_progress', 'completed', 'expired')",
            name="check_exam_status",
        ),
    )
    op.create_index("idx_exams_user", "exams", ["user_id"])

    # ──────────────────────────────────────
    # 7. attempts table
    # ──────────────────────────────────────
    op.create_table(
        "attempts",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "exam_id",
            UUID(as_uuid=True),
            sa.ForeignKey("exams.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("start_time", TIMESTAMP(timezone=True), nullable=True),
        sa.Column("end_time", TIMESTAMP(timezone=True), nullable=True),
        sa.Column("submitted", sa.Boolean(), server_default="false"),
        sa.Column("auto_submitted", sa.Boolean(), server_default="false"),
        sa.Column("responses", sa.JSON(), server_default="{}"),
        sa.Column("question_statuses", sa.JSON(), server_default="{}"),
        sa.Column("events_log", sa.JSON(), server_default="[]"),
        sa.Column("score", sa.Double(), nullable=True),
        sa.Column("max_score", sa.Integer(), server_default="100"),
        sa.Column("total_correct", sa.Integer(), nullable=True),
        sa.Column("total_wrong", sa.Integer(), nullable=True),
        sa.Column("total_unanswered", sa.Integer(), nullable=True),
        sa.Column("score_breakdown", sa.JSON(), nullable=True),
        sa.Column("topic_analysis", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_attempts_user", "attempts", ["user_id"])
    op.create_index("idx_attempts_exam", "attempts", ["exam_id"])

    # ──────────────────────────────────────
    # 8. user_analytics table
    # ──────────────────────────────────────
    op.create_table(
        "user_analytics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("paper", sa.String(10), nullable=True),
        sa.Column("total_exams_taken", sa.Integer(), server_default="0"),
        sa.Column("average_score", sa.Double(), nullable=True),
        sa.Column("best_score", sa.Double(), nullable=True),
        sa.Column("worst_score", sa.Double(), nullable=True),
        sa.Column("topic_proficiency", sa.JSON(), nullable=True),
        sa.Column("score_history", sa.JSON(), nullable=True),
        sa.Column("weak_topics", sa.JSON(), nullable=True),
        sa.Column("strong_topics", sa.JSON(), nullable=True),
        sa.Column(
            "updated_at",
            TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_user_analytics_user", "user_analytics", ["user_id"])

    # ──────────────────────────────────────
    # 9. pgvector IVFFlat indexes
    #    NOTE: IVFFlat needs data rows to build.
    #    For an empty table, use HNSW or create
    #    IVFFlat later after loading data.
    #    We use HNSW here — works on empty tables.
    # ──────────────────────────────────────
    op.execute(
        """
        CREATE INDEX idx_pyq_embedding
        ON pyq_questions
        USING hnsw (embedding vector_cosine_ops)
        """
    )
    op.execute(
        """
        CREATE INDEX idx_qbank_embedding
        ON question_bank
        USING hnsw (embedding vector_cosine_ops)
        """
    )


def downgrade() -> None:
    # Drop in reverse order (respect foreign keys)
    op.execute("DROP INDEX IF EXISTS idx_qbank_embedding")
    op.execute("DROP INDEX IF EXISTS idx_pyq_embedding")

    op.drop_index("idx_user_analytics_user", table_name="user_analytics")
    op.drop_table("user_analytics")

    op.drop_index("idx_attempts_exam", table_name="attempts")
    op.drop_index("idx_attempts_user", table_name="attempts")
    op.drop_table("attempts")

    op.drop_index("idx_exams_user", table_name="exams")
    op.drop_table("exams")

    op.drop_index("ix_qbank_topic", table_name="question_bank")
    op.drop_index("ix_qbank_section_name", table_name="question_bank")
    op.drop_index("ix_qbank_paper", table_name="question_bank")
    op.drop_index("idx_qbank_difficulty", table_name="question_bank")
    op.drop_index("idx_qbank_paper_topic", table_name="question_bank")
    op.drop_table("question_bank")

    op.drop_index("ix_pyq_topic", table_name="pyq_questions")
    op.drop_index("ix_pyq_year", table_name="pyq_questions")
    op.drop_index("ix_pyq_paper", table_name="pyq_questions")
    op.drop_index("idx_pyq_paper_topic", table_name="pyq_questions")
    op.drop_table("pyq_questions")

    op.drop_index("ix_source_documents_paper", table_name="source_documents")
    op.drop_table("source_documents")

    op.drop_index("ix_syllabus_topic", table_name="syllabus")
    op.drop_index("ix_syllabus_section_name", table_name="syllabus")
    op.drop_index("ix_syllabus_paper", table_name="syllabus")
    op.drop_table("syllabus")

    op.execute("DROP EXTENSION IF EXISTS vector")