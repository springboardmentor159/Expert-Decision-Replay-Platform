from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.decision_status import DecisionStatus


class DecisionCreate(BaseModel):
    title: str
    problem_statement: str
    category: str
    rationale: Optional[str] = None


class DecisionUpdate(BaseModel):
    title: Optional[str] = None
    problem_statement: Optional[str] = None
    category: Optional[str] = None
    rationale: Optional[str] = None


class DecisionStatusUpdate(BaseModel):
    status: DecisionStatus


class DecisionResponse(BaseModel):
    id: int
    title: str
    problem_statement: str
    category: str
    rationale: Optional[str] = None
    status: DecisionStatus
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True