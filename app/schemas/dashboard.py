from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.schemas.activity import ActivityResponse


# ---------------------------------------------------------------------
# Employee
# ---------------------------------------------------------------------

class EmployeeDashboardResponse(BaseModel):
    total_decisions: int
    draft_decisions: int
    under_review: int
    approved_decisions: int
    rejected_decisions: int
    pending_reviews: int
    recent_activities: list[ActivityResponse]


class EmployeeDecisionItem(BaseModel):
    id: int
    title: str
    category: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------

class ManagerDashboardResponse(BaseModel):
    team_decisions: int
    pending_approvals: int
    approved_decisions: int
    rejected_decisions: int
    under_review: int


class ManagerStatisticsResponse(BaseModel):
    total_decisions: int
    draft_decisions: int
    under_review: int
    approved_decisions: int
    rejected_decisions: int
    archived_decisions: int


class PendingApprovalItem(BaseModel):
    decision_id: int
    decision_title: str
    approval_id: int
    level: int
    reviewer_id: int
    status: str
    created_at: datetime


# ---------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------

class AdminDashboardResponse(BaseModel):
    total_users: int
    total_decisions: int
    total_approvals: int
    pending_approvals: int
    approved_decisions: int
    rejected_decisions: int
    under_review: int
    draft_decisions: int
    archived_decisions: int
    recent_activities: list[ActivityResponse]


class DecisionStatsBlock(BaseModel):
    total_decisions: int
    draft_decisions: int
    under_review: int
    approved_decisions: int
    rejected_decisions: int
    archived_decisions: int


class UserStatsBlock(BaseModel):
    total_users: int
    active_users: int
    users_by_role: dict[str, int]


class ApprovalStatsBlock(BaseModel):
    total_approvals: int
    pending_approvals: int
    approved_approvals: int
    rejected_approvals: int


class AnalyticsResponse(BaseModel):
    decision_stats: DecisionStatsBlock
    user_stats: UserStatsBlock
    approval_stats: ApprovalStatsBlock


class ApprovalPerformanceResponse(BaseModel):
    average_approval_time_hours: Optional[float] = None
    fastest_approval_hours: Optional[float] = None
    slowest_approval_hours: Optional[float] = None
    pending_approvals: int


class CompletionRateResponse(BaseModel):
    total_approvals: int
    completed_approvals: int
    completion_rate: float


class ActiveUserItem(BaseModel):
    user_id: int
    full_name: str
    role: str
    last_activity_at: datetime
    activity_count: int
