from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


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


class DecisionUpdate(BaseModel):
    title: str | None = None
    problem_statement: str | None = None
    category: str | None = None


class DecisionStatusUpdate(BaseModel):
    status: DecisionStatus


class DecisionRationaleUpdate(BaseModel):
    rationale: str


class DecisionResponse(BaseModel):
    id: int
    title: str
    problem_statement: str
    category: str
    status: DecisionStatus
    created_by: int
    rationale: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True