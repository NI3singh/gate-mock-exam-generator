from datetime import datetime

from pydantic import BaseModel


class QuestionBankBrowserItem(BaseModel):
    id: str
    paper: str
    question_type: str
    marks: int
    difficulty: str
    section_name: str
    topic: str
    stem_tex: str
    code_snippet: str | None = None
    code_language: str | None = None
    choices: list[str] | None = None
    answer: dict
    solution_tex: str
    estimated_time_seconds: int | None = None
    generated_at: datetime | None = None


class QuestionBankBrowserResponse(BaseModel):
    items: list[QuestionBankBrowserItem]
    page: int
    page_size: int
    total: int
    total_pages: int
