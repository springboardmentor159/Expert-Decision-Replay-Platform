from enum import Enum
from datetime import datetime

from pydantic import BaseModel, ConfigDict


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
    title: str
    problem_statement: str
    category: str


# -----------------------------------------
# Update Decision
# -----------------------------------------

class DecisionUpdate(BaseModel):
    title: str
    problem_statement: str
    category: str


# -----------------------------------------
# Update Decision Status
# -----------------------------------------

class DecisionStatusUpdate(BaseModel):
    status: DecisionStatus


# -----------------------------------------
# Decision Rationale Update
# -----------------------------------------

class DecisionRationaleUpdate(BaseModel):
    rationale: str


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