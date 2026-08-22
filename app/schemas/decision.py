from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


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

    class Config:
        from_attributes = True
