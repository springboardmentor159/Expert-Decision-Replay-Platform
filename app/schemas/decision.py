from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class DecisionStatus(str, Enum):
    """Enum for Decision status values"""
    Draft = "Draft"
    UnderReview = "Under Review"
    Approved = "Approved"
    Rejected = "Rejected"
    Archived = "Archived"


class DecisionBase(BaseModel):
    """Base schema for Decision data"""
    title: str
    problem_statement: str
    category: str


class DecisionCreate(DecisionBase):
    """Schema for creating a new decision"""
    pass


class DecisionUpdate(BaseModel):
    """Schema for updating a decision"""
    title: str | None = None
    problem_statement: str | None = None
    category: str | None = None


class DecisionStatusUpdate(BaseModel):
    """Schema for updating decision status"""
    status: DecisionStatus


class DecisionRationaleUpdate(BaseModel):
    """Schema for updating decision rationale"""
    rationale: str


class DecisionResponse(DecisionBase):
    """Schema for decision response"""
    id: int
    status: str
    rationale: str | None = None
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DecisionFilterResponse(BaseModel):
    """Schema for filtered decision responses"""
    decisions: list[DecisionResponse]
    total: int
