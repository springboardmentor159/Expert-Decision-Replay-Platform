from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class ApprovalStatus(str, Enum):
    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"


class ApprovalCreate(BaseModel):
    decision_id: int
    assigned_to: int
    approval_level: int = 1


class ApprovalResponse(BaseModel):
    id: int
    decision_id: int
    assigned_to: int
    approval_level: int
    status: ApprovalStatus
    created_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)