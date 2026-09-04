from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.approval import ApprovalStatus


class ApprovalCreate(BaseModel):
    decision_id: int
    reviewer_id: int


class ApprovalStatusUpdate(BaseModel):
    status: ApprovalStatus


class ApprovalResponse(BaseModel):
    id: int
    decision_id: int
    reviewer_id: int
    status: ApprovalStatus
    created_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )
