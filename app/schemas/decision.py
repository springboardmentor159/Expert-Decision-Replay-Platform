from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class DecisionStatus(str, Enum):
    DRAFT = "Draft"
    UNDER_REVIEW = "Under Review"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    ARCHIVED = "Archived"


class DecisionCategory(str, Enum):
    AI_TESTING = "AI Testing"
    CLOUD = "Cloud"
    TECHNOLOGY = "Technology"
    TESTING = "Testing"


class DecisionCreate(BaseModel):
    title: str
    problem_statement: str
    category: DecisionCategory


class DecisionUpdate(BaseModel):
    title: str
    problem_statement: str
    category: DecisionCategory


class DecisionStatusUpdate(BaseModel):
    status: DecisionStatus


class DecisionResponse(BaseModel):
    id: int
    title: str
    problem_statement: str
    category: DecisionCategory
    status: str
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class DecisionVersionResponse(BaseModel):
    decision_id: int
    version_number: int
    title: str
    problem_statement: str
    description: str | None
    category: str
    status: str
    created_by: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }