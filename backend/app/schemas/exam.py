from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator


# ── Existing schemas (unchanged) ──────────────────────────────────────────────

class TypesRatio(BaseModel):
    MCQ: float = 0.6
    MSQ: float = 0.2
    NAT: float = 0.2

    @field_validator("MCQ", "MSQ", "NAT")
    @classmethod
    def validate_ratio(cls, v: float) -> float:
        if v < 0 or v > 1:
            raise ValueError("Ratio values must be between 0 and 1")
        return v


class ExamGenerateRequest(BaseModel):
    paper: str
    scope: str  # 'full' or 'topic'
    selected_topics: Optional[list[str]] = None
    difficulty: str  # 'easy', 'medium', 'hard', 'auto'
    types_ratio: TypesRatio = TypesRatio()
    # Inject real previous-year questions into generation prompts as style /
    # difficulty reference (no-op when no PYQs are loaded for the paper).
    use_pyq_reference: bool = True

    @field_validator("paper")
    @classmethod
    def validate_paper(cls, v: str) -> str:
        v = v.upper()
        if v not in ("CS", "DA"):
            raise ValueError("paper must be 'CS' or 'DA'")
        return v

    @field_validator("scope")
    @classmethod
    def validate_scope(cls, v: str) -> str:
        v = v.lower()
        if v not in ("full", "topic"):
            raise ValueError("scope must be 'full' or 'topic'")
        return v

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        v = v.lower()
        if v not in ("easy", "medium", "hard", "auto"):
            raise ValueError("difficulty must be 'easy', 'medium', 'hard', or 'auto'")
        return v

    @field_validator("selected_topics")
    @classmethod
    def validate_selected_topics(cls, v: Optional[list[str]], info) -> Optional[list[str]]:
        return v


class ExamGenerateResponse(BaseModel):
    exam_id: UUID
    status: str
    message: str


class ExamSummary(BaseModel):
    id: UUID
    paper: str
    scope: str
    selected_topics: Optional[list[str]] = None
    difficulty: str
    total_questions: int
    total_marks: int
    duration_minutes: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ExamHistoryItem(BaseModel):
    id: UUID
    paper: str
    scope: str
    selected_topics: Optional[list[str]] = None
    difficulty: str
    total_questions: int
    total_marks: int
    duration_minutes: int
    status: str
    score: Optional[float] = None
    max_score: int = 100
    attempt_id: Optional[str] = None
    created_at: datetime


class ExamHistoryResponse(BaseModel):
    items: list[ExamHistoryItem]
    page: int
    page_size: int
    total: int
    total_pages: int


# ── Part 8: Exam screen schemas ───────────────────────────────────────────────

class QuestionItem(BaseModel):
    """
    Single question for the exam screen.
    CRITICAL: Does NOT contain the answer field.
    """
    id: str
    qno: int
    question_type: str          # 'MCQ', 'MSQ', 'NAT'
    marks: int                  # 1 or 2
    section: str                # 'GA' or 'Subject'
    section_name: str           # e.g. 'General Aptitude', 'Linear Algebra'
    topic: str
    stem_tex: str               # Question text with LaTeX math
    code_snippet: Optional[str] = None
    code_language: Optional[str] = None
    choices: Optional[list[str]] = None   # 4 choices for MCQ/MSQ, null for NAT
    estimated_time_seconds: Optional[int] = None


class ExamScreenResponse(BaseModel):
    """Full exam data returned for the exam screen."""
    exam_id: str
    paper: str
    difficulty: str
    total_questions: int
    total_marks: int
    duration_minutes: int
    questions: list[QuestionItem]   # Ordered by qno, NO answers


class AttemptStartResponse(BaseModel):
    """
    Response from POST /exams/{id}/start.
    Returns attempt ID, server start time, and any saved responses for resume.
    """
    attempt_id: str
    exam_id: str
    start_time: str         # ISO 8601 datetime string
    remaining_seconds: int  # Seconds left in the exam
    responses: dict         # Previously saved responses (for resume)
    question_statuses: dict # Previously saved statuses (for resume)
    submitted: bool         # True if already submitted (should not reach exam screen)
    is_resume: bool = False # True if resuming an existing attempt
