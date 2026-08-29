from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ActivityResponse(BaseModel):
    id: int
    user_id: int | None
    action: str
    entity_type: str
    entity_id: int | None
    description: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ApprovalResponse(BaseModel):
    id: int
    decision_id: int
    approval_level: int
    reviewer_id: int
    status: str
    created_at: datetime
    completed_at: datetime | None
    model_config = ConfigDict(from_attributes=True)


class PaginatedActivityResponse(BaseModel):
    items: list[ActivityResponse]
    page: int
    page_size: int
    total: int


class ApprovalCreate(BaseModel):
    decision_id: int
    reviewer_id: int
    approval_level: int = Field(default=1, ge=1)


class ApprovalDecision(BaseModel):
    decision: str