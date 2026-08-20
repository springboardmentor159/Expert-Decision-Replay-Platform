from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


# Official Decision statuses
DecisionStatus = Literal[
    "Draft",
    "Under Review",
    "Approved",
    "Rejected",
    "Archived",
]


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

    model_config = ConfigDict(from_attributes=True)