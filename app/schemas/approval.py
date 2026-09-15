from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.approval import ApprovalStatus


class ApprovalCreate(BaseModel):
    decision_id: int
    reviewer_id: int
    sequence_order: int = 1
    due_date: datetime | None = None


class ApprovalStatusUpdate(BaseModel):
    status: ApprovalStatus


class ApprovalEscalateRequest(BaseModel):
    escalated_to_id: int | None = None
    reason: str | None = None


class ApprovalResponse(BaseModel):
    id: int
    decision_id: int
    reviewer_id: int
    status: ApprovalStatus
    sequence_order: int = 1
    due_date: datetime | None = None
    is_escalated: int = 0
    escalated_to_id: int | None = None
    created_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )

