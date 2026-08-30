from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime


class ActivityOut(BaseModel):
    id: int
    user_id: int
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmployeeDashboard(BaseModel):
    total_decisions: int
    draft_decisions: int
    under_review: int
    approved_decisions: int
    rejected_decisions: int
    pending_reviews: int
    recent_activities: List[ActivityOut]


class ManagerDashboard(BaseModel):
    team_decisions: int
    pending_approvals: int
    approved_decisions: int
    rejected_decisions: int
    under_review: int


class AdminDashboard(BaseModel):
    total_users: int
    total_decisions: int
    pending_approvals: int
    approved_decisions: int
    rejected_decisions: int
    under_review: int
    total_approvals: int
    completion_rate: float