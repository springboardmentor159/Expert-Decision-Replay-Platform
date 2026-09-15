from enum import Enum
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator
)


# -----------------------------------------
# Decision Status
# -----------------------------------------


class DecisionStatus(str, Enum):
    DRAFT = "Draft"
    UNDER_REVIEW = "Under Review"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    ARCHIVED = "Archived"


# -----------------------------------------
# Create Decision
# -----------------------------------------


class DecisionCreate(BaseModel):
    title: str = Field(..., min_length=1)
    problem_statement: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)

    @field_validator(
        "title",
        "problem_statement",
        "category"
    )
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty")

        return value


# -----------------------------------------
# Update Decision
# -----------------------------------------


class DecisionUpdate(BaseModel):
    title: str = Field(..., min_length=1)
    problem_statement: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)

    @field_validator(
        "title",
        "problem_statement",
        "category"
    )
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty")

        return value


# -----------------------------------------
# Update Decision Status
# -----------------------------------------


class DecisionStatusUpdate(BaseModel):
    status: DecisionStatus


# -----------------------------------------
# Decision Rationale Update
# -----------------------------------------


class DecisionRationaleUpdate(BaseModel):
    rationale: str = Field(..., min_length=1)

    @field_validator("rationale")
    @classmethod
    def validate_rationale(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Rationale cannot be empty")

        return value


# -----------------------------------------
# Decision Response
# -----------------------------------------


class DecisionResponse(BaseModel):
    id: int
    title: str
    problem_statement: str
    category: str
    status: str
    created_by: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )