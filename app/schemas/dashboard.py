from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ActivityResponse(BaseModel):
    action: str
    entity_type: str
    entity_id: int
    description: str
    user_id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class EmployeeDashboardResponse(BaseModel):
    total_decisions: int
    draft_decisions: int
    under_review: int
    approved_decisions: int
    rejected_decisions: int
    pending_reviews: int
    recent_activities: list[ActivityResponse]
