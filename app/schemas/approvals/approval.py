from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


ApprovalStatus = Literal[
    "Pending",
    "Under Review",
    "Approved",
    "Rejected",
]

ApprovalLevel = Literal[1, 2]


class ApprovalCreate(BaseModel):
    decision_id: int = Field(ge=1)
    reviewer_id: int = Field(ge=1)
    approval_level: ApprovalLevel
    status: ApprovalStatus = "Pending"


class ApprovalUpdate(BaseModel):
    status: Optional[ApprovalStatus] = None
    completed_at: Optional[datetime] = None


class ApprovalResponse(BaseModel):
    id: int
    decision_id: int
    reviewer_id: int
    approval_level: ApprovalLevel
    status: ApprovalStatus
    assigned_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True