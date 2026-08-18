from enum import Enum

from pydantic import BaseModel, ConfigDict


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
    status: str
    created_by: int
    created_at: object
    updated_at: object

    model_config = ConfigDict(from_attributes=True)