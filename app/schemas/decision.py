from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.decision import DecisionStatus


class DecisionCreate(BaseModel):
    title: str
    problem_statement: str
    category: str


class DecisionUpdate(BaseModel):
    title: str
    problem_statement: str
    category: str


class DecisionRationaleUpdate(BaseModel):
    rationale: str


class DecisionStatusUpdate(BaseModel):
    status: DecisionStatus


class DecisionResponse(BaseModel):
    id: int
    title: str
    problem_statement: str
    rationale: str | None
    category: str
    status: DecisionStatus
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )