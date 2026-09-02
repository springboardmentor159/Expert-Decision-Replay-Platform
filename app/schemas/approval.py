from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ApprovalCreate(BaseModel):
    decision_id: int
    assigned_reviewer_id: int
    approval_level: int = 1


class ApprovalResponse(BaseModel):
    id: int
    decision_id: int
    assigned_reviewer_id: int
    approval_level: int
    status: str
    created_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ApprovalAction(BaseModel):
    status: str