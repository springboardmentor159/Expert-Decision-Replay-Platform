from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ApprovalStatus(str, Enum):
    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"


class ApprovalCreate(BaseModel):
    reviewer_id: int = Field(gt=0)


class ApprovalAction(BaseModel):
    status: ApprovalStatus
    comments: str | None = None


class ApprovalResponse(BaseModel):
    id: int
    decision_id: int
    reviewer_id: int
    status: str
    comments: str | None = None
    created_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
