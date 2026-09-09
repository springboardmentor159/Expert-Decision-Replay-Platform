from datetime import datetime

from pydantic import BaseModel

from app.models.decision_status import DecisionStatus


class DecisionVersionResponse(BaseModel):
    id: int
    decision_id: int
    version_number: int
    title: str
    problem_statement: str
    description: str | None = None
    category: str | None = None
    status: DecisionStatus
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True