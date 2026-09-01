from datetime import datetime

from pydantic import BaseModel


class ApprovalCreate(BaseModel):
    decision_id: int
    reviewer_id: int
    approval_level: int = 1


class ApprovalResponse(BaseModel):
    id: int
    decision_id: int
    reviewer_id: int
    approval_level: int
    status: str
    created_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True