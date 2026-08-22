from datetime import datetime
from enum import Enum

from pydantic import BaseModel


# CREATE DECISION
class DecisionCreate(BaseModel):
    title: str
    problem_statement: str
    category: str


# UPDATE DECISION
class DecisionUpdate(BaseModel):
    title: str
    problem_statement: str
    category: str


# DECISION STATUS
class DecisionStatus(str, Enum):
    Draft = "Draft"
    Approved = "Approved"
    Rejected = "Rejected"


# UPDATE STATUS
class DecisionStatusUpdate(BaseModel):
    status: DecisionStatus


# RESPONSE
class DecisionResponse(BaseModel):
    id: int
    title: str
    problem_statement: str
    category: str
    status: str
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
