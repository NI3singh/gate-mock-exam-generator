from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator


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
        # Will be validated against DB in the endpoint
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