from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
from enum import Enum

from app.schemas.tag import TagResponse


class DecisionStatus(str, Enum):
    DRAFT = "Draft"
    UNDER_REVIEW = "Under Review"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    ARCHIVED = "Archived"


class DecisionCreate(BaseModel):
    title: str
    problem_statement: str
    category: str


# Fields the client is allowed to update.
# id, created_by, created_at are intentionally NOT here —
# they are controlled by the backend/database.
class DecisionUpdate(BaseModel):
    title: Optional[str] = None
    problem_statement: Optional[str] = None
    category: Optional[str] = None


class DecisionStatusUpdate(BaseModel):
    status: DecisionStatus


# Sprint 7: Decision Rationale
class DecisionRationaleUpdate(BaseModel):
    rationale: str


class DecisionRationaleResponse(BaseModel):
    decision_id: int
    rationale: Optional[str] = None

    class Config:
        from_attributes = True


class DecisionResponse(BaseModel):
    id: int
    title: str
    problem_statement: str
    category: str
    status: DecisionStatus
    rationale: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: datetime
    tags: list[TagResponse] = []

    class Config:
        from_attributes = True


# Sprint 9: Knowledge Repository / Search
class DecisionSearchResult(BaseModel):
    """Lightweight representation returned by search & list endpoints."""
    id: int
    title: str
    category: str
    status: DecisionStatus
    tags: list[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @field_validator("tags", mode="before")
    @classmethod
    def _extract_tag_names(cls, value):
        # ORM gives us Tag objects (value.name); plain lists of strings
        # (e.g. in tests) are passed through unchanged.
        if value and hasattr(value[0], "name"):
            return [tag.name for tag in value]
        return value


class PaginatedDecisions(BaseModel):
    items: list[DecisionSearchResult]
    page: int
    page_size: int
    total: int


class TimelineEvent(BaseModel):
    event_type: str
    description: str
    timestamp: datetime


class DecisionTimelineResponse(BaseModel):
    decision_id: int
    timeline: list[TimelineEvent]
