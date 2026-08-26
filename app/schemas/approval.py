from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ApprovalStatus(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class ApprovalCreate(BaseModel):
    decision_id: int
    reviewer_id: int
    approval_level: Optional[int] = 1
    comments: Optional[str] = None


class ApprovalAction(BaseModel):
    comments: Optional[str] = None


class ApprovalResponse(BaseModel):
    id: int
    decision_id: int
    reviewer_id: int
    status: str
    approval_level: int
    comments: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
