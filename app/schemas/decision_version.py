from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DecisionVersionListItem(BaseModel):
    """Lightweight row for GET /decisions/{id}/versions."""
    version_number: int
    title: str
    status: str
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class DecisionVersionDetail(BaseModel):
    """Full snapshot for GET /decisions/{id}/versions/{version_number}."""
    decision_id: int
    version_number: int
    title: str
    problem_statement: str
    category: str
    status: str
    rationale: Optional[str] = None
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class HistoryEvent(BaseModel):
    event_type: str
    description: str
    actor_id: Optional[int] = None
    timestamp: datetime


class DecisionHistoryResponse(BaseModel):
    decision_id: int
    history: list[HistoryEvent]
