from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ActivityItem(BaseModel):
    id: int
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StatusCount(BaseModel):
    status: str
    count: int


class EmployeeDashboard(BaseModel):
    user_id: int
    total_decisions: int
    decisions_by_status: List[StatusCount]
    recent_activity: List[ActivityItem]


class ManagerStatistics(BaseModel):
    scope: str
    total: int
    draft: int
    under_review: int
    approved: int
    rejected: int
    archived: int
