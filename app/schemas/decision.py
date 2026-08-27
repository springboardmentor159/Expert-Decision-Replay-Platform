from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, field_validator


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
    tags: list[str] = []

    model_config = ConfigDict(from_attributes=True)

    @field_validator("tags", mode="before")
    @classmethod
    def convert_tags(cls, value):
        if value is None:
            return []

        return [
            tag.name if hasattr(tag, "name") else tag
            for tag in value
        ]