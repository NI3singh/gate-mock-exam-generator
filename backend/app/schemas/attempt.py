from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AttemptSaveRequest(BaseModel):
    responses: dict[str, Any]
    question_statuses: dict[str, Any]


class AttemptSaveResponse(BaseModel):
    saved: bool
    timestamp: str  # ISO datetime string


class AttemptEventRequest(BaseModel):
    event_type: str
    detail: str | None = None
    timestamp: str  # ISO datetime string


class AttemptEventResponse(BaseModel):
    logged: bool


class AttemptSubmitResponse(BaseModel):
    attempt_id: str
    exam_id: str
    paper: str
    difficulty: str
    total_questions: int
    total_marks: int
    duration_minutes: int
    score: float
    max_score: int
    total_correct: int
    total_wrong: int
    total_unanswered: int
    score_breakdown: dict
    section_scores: dict
    topic_analysis: list
    violations_count: int


# ── Solution & Violation schemas (Part 11) ─────────────────────────────────────

class SolutionItem(BaseModel):
    qno: int
    question_type: str
    marks: int
    section: str
    section_name: str
    topic: str
    stem_tex: str
    code_snippet: str | None = None
    code_language: str | None = None
    choices: list[str] | None = None
    user_answer: dict | None = None
    correct_answer: dict
    is_correct: bool
    score: float
    solution_tex: str


class ViolationSummary(BaseModel):
    event_type: str
    count: int


class AttemptDetailResponse(BaseModel):
    attempt_id: str
    exam_id: str
    paper: str
    difficulty: str
    total_questions: int
    total_marks: int
    duration_minutes: int
    score: float
    max_score: int
    total_correct: int
    total_wrong: int
    total_unanswered: int
    negative_marks: float
    score_breakdown: dict
    section_scores: dict
    topic_analysis: list
    violations: list[ViolationSummary]
    violations_count: int
    solutions: list[SolutionItem]
