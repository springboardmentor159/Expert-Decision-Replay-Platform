from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ApprovalCreate(BaseModel):
    decision_id: int
    reviewer_id: int
    approval_level: int = 1


class ApprovalAction(BaseModel):
    status: str


class ApprovalResponse(BaseModel):
    id: int
    decision_id: int
    reviewer_id: int
    approval_level: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True