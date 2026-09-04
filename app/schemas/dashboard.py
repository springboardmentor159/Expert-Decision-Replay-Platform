from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ============================================================
# EMPLOYEE SCHEMAS
# ============================================================

class EmployeeDecisionSummary(BaseModel):
    id: int
    title: str
    category: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmployeeActivitySummary(BaseModel):
    id: int
    user_id: int
    action: str
    entity_type: str
    entity_id: int | None
    description: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmployeePendingReview(BaseModel):
    id: int
    decision_id: int
    decision_title: str
    approval_level: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmployeeDashboardResponse(BaseModel):
    my_decisions: int
    draft_decisions: int
    decisions_under_review: int
    approved_decisions: int
    rejected_decisions: int
    pending_reviews: int
    recent_activities: list[EmployeeActivitySummary]


# ============================================================
# MANAGER SCHEMAS
# ============================================================

class ManagerDecisionSummary(BaseModel):
    id: int
    title: str
    category: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ManagerPendingApproval(BaseModel):
    id: int
    decision_id: int
    decision_title: str
    approval_level: str
    assigned_to: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ManagerDashboardResponse(BaseModel):
    team_decisions: int
    pending_approvals: int
    approved_decisions: int
    rejected_decisions: int
    under_review: int
    recent_team_activities: list[EmployeeActivitySummary]


class ManagerStatisticsResponse(BaseModel):
    total_decisions: int
    draft_decisions: int
    under_review: int
    approved_decisions: int
    rejected_decisions: int
    archived_decisions: int
# ============================================================
# ADMIN SCHEMAS
# ============================================================

class AdminDashboardResponse(BaseModel):
    total_users: int
    total_decisions: int
    pending_approvals: int
    approved_decisions: int
    rejected_decisions: int
    under_review_decisions: int
    draft_decisions: int
    archived_decisions: int
    recent_system_activities: list[EmployeeActivitySummary]


class AdminAnalyticsResponse(BaseModel):
    total_decisions: int
    draft_decisions: int
    under_review_decisions: int
    approved_decisions: int
    rejected_decisions: int
    archived_decisions: int
    total_users: int
    users_by_role: dict[str, int]
    total_approvals: int
    pending_approvals: int
    completed_approvals: int


class DecisionActivityResponse(BaseModel):
    period: str
    count: int


class ApprovalStatisticsResponse(BaseModel):
    average_approval_time_hours: float
    fastest_approval_time_hours: float | None
    slowest_approval_time_hours: float | None
    pending_approvals: int


class ApprovalCompletionRateResponse(BaseModel):
    total_approvals: int
    completed_approvals: int
    completion_rate: float


class UserActivityResponse(BaseModel):
    user_id: int
    user_name: str
    action: str
    entity_type: str
    entity_id: int | None
    description: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
