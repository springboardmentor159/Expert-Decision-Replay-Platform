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