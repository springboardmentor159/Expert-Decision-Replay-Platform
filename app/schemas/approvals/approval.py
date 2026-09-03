from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ApprovalCreate(BaseModel):
    decision_id: int
    reviewer_id: int
    approval_level: int = Field(ge=1)
    status: str = "Pending"


class ApprovalUpdate(BaseModel):
    status: Optional[str] = None
    completed_at: Optional[datetime] = None


class ApprovalResponse(BaseModel):
    id: int
    decision_id: int
    reviewer_id: int
    approval_level: int
    status: str
    assigned_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True