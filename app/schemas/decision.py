from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DecisionStatus(str, Enum):
    DRAFT = "Draft"
    UNDER_REVIEW = "Under Review"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    ARCHIVED = "Archived"


class DecisionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    problem_statement: str = Field(min_length=1)
    category: str = Field(min_length=1, max_length=100)


class DecisionUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    problem_statement: Optional[str] = Field(default=None, min_length=1)
    category: Optional[str] = Field(default=None, min_length=1, max_length=100)


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