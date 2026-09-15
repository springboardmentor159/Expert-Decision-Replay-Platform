from datetime import datetime

from pydantic import BaseModel


class ApprovalCreate(BaseModel):
    decision_id: int
    reviewer_id: int
    approval_level: int = 1
    due_at: datetime | None = None


class ApprovalResponse(BaseModel):
    id: int
    decision_id: int
    reviewer_id: int
    approval_level: int
    status: str
    created_at: datetime
    completed_at: datetime | None = None

    due_at: datetime | None = None
    escalated: bool = False
    escalated_at: datetime | None = None
    escalation_reason: str | None = None

    class Config:
        from_attributes = True