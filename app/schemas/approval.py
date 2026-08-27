from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class ApprovalStatus(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class ApprovalCreate(BaseModel):
    """Assign a decision to a reviewer for approval."""
    reviewer_id: int
    level: int = 1


class ApprovalActionRequest(BaseModel):
    """Reviewer approves or rejects."""
    decision: ApprovalStatus  # must be APPROVED or REJECTED
    comments: Optional[str] = None


class ApprovalResponse(BaseModel):
    id: int
    decision_id: int
    level: int
    reviewer_id: int
    status: ApprovalStatus
    comments: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
