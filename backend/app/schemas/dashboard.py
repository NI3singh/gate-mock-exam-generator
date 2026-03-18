from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class RecentExam(BaseModel):
    id: UUID
    paper: str
    scope: str
    difficulty: str
    total_questions: int
    total_marks: int
    status: str
    score: Optional[float] = None
    max_score: int = 100
    created_at: datetime


class DashboardStats(BaseModel):
    total_exams_taken: int = 0
    average_score: Optional[float] = None
    best_score: Optional[float] = None
    worst_score: Optional[float] = None
    total_questions_attempted: int = 0
    recent_exams: list[RecentExam] = []