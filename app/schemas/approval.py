from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class ApprovalStatus(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class ApprovalLevel(str, Enum):
    REVIEWER = "Reviewer"
    MANAGER = "Manager"


class ApprovalResponse(BaseModel):
    id: int
    decision_id: int
    assigned_to: int
    approval_level: ApprovalLevel
    status: ApprovalStatus
    created_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)