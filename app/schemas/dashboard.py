from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ActivityItem(BaseModel):
    id: int
    user_id: int
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


class UserRoleCount(BaseModel):
    role: str
    count: int


class UserStats(BaseModel):
    total: int
    active: int
    by_role: List[UserRoleCount]


class DecisionStats(BaseModel):
    total: int
    draft: int
    under_review: int
    approved: int
    rejected: int
    archived: int


class ApprovalStats(BaseModel):
    total: int
    pending: int
    approved: int
    rejected: int


class AdminDashboard(BaseModel):
    total_users: int
    total_decisions: int
    decision_stats: DecisionStats
    approval_stats: Optional[ApprovalStats]
    recent_activity: List[ActivityItem]


class AdminAnalytics(BaseModel):
    decision_stats: DecisionStats
    user_stats: UserStats
    approval_stats: Optional[ApprovalStats]


class DecisionActivityItem(BaseModel):
    period: str
    count: int


class AdminDecisionActivity(BaseModel):
    granularity: str
    data: List[DecisionActivityItem]


class ApprovalStatisticsResponse(BaseModel):
    """BLOCKED: approval workflow not implemented. Returned as 501."""
    detail: str = "Approval statistics unavailable: approval workflow not implemented"


class UserActivitySummary(BaseModel):
    user_id: int
    full_name: str
    email: str
    role: str
    total_actions: int
    actions_by_type: dict
    last_active: Optional[datetime] = None


class AdminUserActivity(BaseModel):
    total_active_users: int
    users: List[UserActivitySummary]


class PaginatedActivityResponse(BaseModel):
    items: List[ActivityItem]
    total: int
    offset: int
    limit: int
    has_more: bool
