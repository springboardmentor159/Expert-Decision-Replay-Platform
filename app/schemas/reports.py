from datetime import datetime

from pydantic import BaseModel, ConfigDict


# =========================================================
# DECISION REPORTS
# =========================================================

class DecisionReportItem(BaseModel):
    id: int
    title: str
    category: str
    status: str
    creator_id: int
    creator_name: str
    created_at: datetime
    updated_at: datetime
    alternative_count: int
    approval_count: int
    tags: list[str]

    model_config = ConfigDict(from_attributes=True)


class DecisionReportStats(BaseModel):
    total: int
    draft: int
    under_review: int
    approved: int
    rejected: int
    archived: int


class DecisionReportResponse(BaseModel):
    items: list[DecisionReportItem]
    stats: DecisionReportStats
    page: int
    page_size: int
    total: int


# =========================================================
# APPROVAL REPORTS
# =========================================================

class ApprovalReportItem(BaseModel):
    id: int
    decision_id: int
    decision_title: str
    reviewer_id: int
    reviewer_name: str
    approval_level: str
    status: str
    created_at: datetime
    completed_at: datetime | None
    turnaround_hours: float | None

    model_config = ConfigDict(from_attributes=True)


class ApprovalReportStats(BaseModel):
    total: int
    pending: int
    approved: int
    rejected: int
    average_turnaround_hours: float | None
    completion_rate: float


class ApprovalReportResponse(BaseModel):
    items: list[ApprovalReportItem]
    stats: ApprovalReportStats
    page: int
    page_size: int
    total: int
class TeamReportItem(BaseModel):
    team_name: str
    member_count: int
    total_decisions: int
    approved_decisions: int
    rejected_decisions: int
    pending_decisions: int
    total_approvals: int
    approved_approvals: int
    rejected_approvals: int
    pending_approvals: int
    approval_completion_rate: float

    model_config = ConfigDict(from_attributes=True)


class TeamReportResponse(BaseModel):
    items: list[TeamReportItem]
    page: int
    page_size: int
    total: int
class AuditReportItem(BaseModel):
    id: int
    user_id: int
    user_name: str
    action: str
    entity_type: str
    entity_id: int | None
    description: str
    ip_address: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditReportResponse(BaseModel):
    items: list[AuditReportItem]
    page: int
    page_size: int
    total: int
