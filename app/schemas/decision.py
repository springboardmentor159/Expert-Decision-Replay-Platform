from datetime import datetime
from enum import Enum

from pydantic import BaseModel


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
    title: str
    problem_statement: str
    category: str


class DecisionStatusUpdate(BaseModel):
    status: DecisionStatus


class DecisionResponse(BaseModel):
    id: int
    title: str
    problem_statement: str
    category: str
    status: DecisionStatus
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DecisionVersionResponse(BaseModel):
    id: int
    decision_id: int
    version_number: int
    title: str
    problem_statement: str
    description: str | None = None
    category: str
    status: DecisionStatus
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class DecisionVersionListResponse(BaseModel):
    decision_id: int
    versions: list[DecisionVersionResponse]


class DecisionHistoryResponse(BaseModel):
    decision_id: int
    current: DecisionResponse
    history: list[DecisionVersionResponse]
