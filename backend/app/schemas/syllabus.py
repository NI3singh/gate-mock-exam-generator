from pydantic import BaseModel


class TopicItem(BaseModel):
    """Single topic row from the syllabus table."""
    id: int
    topic: str
    subtopic: str | None = None


class SyllabusSection(BaseModel):
    """A section containing a list of topics."""
    section_name: str
    topics: list[TopicItem]


class SyllabusResponse(BaseModel):
    """Full syllabus for a paper, grouped by sections."""
    paper: str
    total_topics: int
    sections: list[SyllabusSection]


class TopicFlat(BaseModel):
    """Flat topic item for checkbox lists."""
    id: int
    section_name: str
    topic: str


class TopicListResponse(BaseModel):
    """Flat list of all topics for a paper."""
    paper: str
    total_topics: int
    topics: list[TopicFlat]


class DataLoadResponse(BaseModel):
    """Response from the data loading endpoint."""
    message: str
    papers_loaded: list[str]
    total_rows_inserted: int
    details: dict
    errors: list[str]


class SyllabusStatsResponse(BaseModel):
    """Quick overview of what's loaded."""
    stats: dict