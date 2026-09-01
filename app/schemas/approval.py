from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.approval_status import ApprovalStatus


class ApprovalCreate(BaseModel):
    reviewer_id: int
    approval_level: int = 1


class ApprovalUpdate(BaseModel):
    status: ApprovalStatus


class ApprovalResponse(BaseModel):
    id: int
    decision_id: int
    reviewer_id: int
    approval_level: int
    status: ApprovalStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True