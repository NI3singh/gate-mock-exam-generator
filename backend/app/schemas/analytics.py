from datetime import datetime

from pydantic import BaseModel


class ScoreHistoryPoint(BaseModel):
    attempt_id: str
    exam_id: str
    paper: str
    score: float
    max_score: float
    percentage: float
    submitted_at: datetime
    label: str


class TopicPerformanceItem(BaseModel):
    topic: str
    section_name: str
    total_questions: int
    correct: int
    wrong: int
    unanswered: int
    score: float
    max_score: float
    accuracy: float
    attempts_covered: int


class AnalyticsDashboardResponse(BaseModel):
    total_exams_taken: int = 0
    average_score: float | None = None
    best_score: float | None = None
    worst_score: float | None = None
    total_questions_attempted: int = 0
    improvement_percentage: float = 0.0
    score_history: list[ScoreHistoryPoint] = []
    weak_topics: list[TopicPerformanceItem] = []
    strong_topics: list[TopicPerformanceItem] = []


class TopicPerformanceResponse(BaseModel):
    topics: list[TopicPerformanceItem] = []
