from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.activity_log import ActivityLogResponse


class EmployeeDashboardResponse(BaseModel):
    total_decisions: int
    draft_decisions: int
    under_review: int
    approved_decisions: int
    rejected_decisions: int
    pending_reviews: int
    recent_activities: List[ActivityLogResponse] = []


class ManagerDashboardResponse(BaseModel):
    team_decisions: int
    pending_approvals: int
    approved_decisions: int
    rejected_decisions: int
    under_review: int
    recent_activities: List[ActivityLogResponse] = []


class ManagerStatisticsResponse(BaseModel):
    total_decisions: int
    draft_decisions: int
    under_review: int
    approved_decisions: int
    rejected_decisions: int
    archived_decisions: int


class AdminDashboardResponse(BaseModel):
    total_users: int
    total_decisions: int
    approved_decisions: int
    rejected_decisions: int
    under_review: int
    archived_decisions: int
    draft_decisions: int
    total_approvals: int
    pending_approvals: int
    recent_activities: List[ActivityLogResponse] = []


class DecisionStats(BaseModel):
    total_decisions: int
    approved_decisions: int
    rejected_decisions: int
    under_review: int
    archived_decisions: int
    draft_decisions: int


class UserStats(BaseModel):
    total_users: int
    active_users: int
    users_by_role: Dict[str, int]


class ApprovalStats(BaseModel):
    total_approvals: int
    pending_approvals: int
    approved_approvals: int
    rejected_approvals: int


class AdminAnalyticsResponse(BaseModel):
    decision_statistics: DecisionStats
    user_statistics: UserStats
    approval_statistics: ApprovalStats


class ApprovalPerformanceResponse(BaseModel):
    total_approvals: int
    completed_approvals: int
    pending_approvals: int
    completion_rate: float
    average_approval_time_hours: Optional[float] = None
    fastest_approval_hours: Optional[float] = None
    slowest_approval_hours: Optional[float] = None


class ActiveUserItem(BaseModel):
    user_id: int
    full_name: str
    email: str
    role: str
    action_count: int
    last_action_at: Optional[datetime] = None


class UserActivityResponse(BaseModel):
    active_users_count: int
    active_users: List[ActiveUserItem]
