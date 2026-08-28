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
    status: ApprovalStatus
    comments: Optional[str] = None


class ApprovalResponse(BaseModel):
    id: int
    decision_id: int
    reviewer_id: int
    approval_level: int
    status: str
    comments: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    decision_title: Optional[str] = None
    reviewer_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
