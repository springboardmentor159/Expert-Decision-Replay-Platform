from datetime import datetime
from pydantic import BaseModel, ConfigDict


# ============================================================
# DECISION REPORT SCHEMAS
# ============================================================

class DecisionReportItem(BaseModel):
    decision_id: int
    decision_title: str
    category: str
    status: str
    created_by: int
    creator_name: str | None = None
    created_date: datetime
    updated_date: datetime
    number_of_alternatives: int
    number_of_approvals: int
    tags: list[str] = []

    model_config = ConfigDict(from_attributes=True)


class DecisionReportSummary(BaseModel):
    total_decisions: int
    draft_decisions: int
    decisions_under_review: int
    approved_decisions: int
    rejected_decisions: int
    archived_decisions: int


class DecisionReportResponse(BaseModel):
    summary: DecisionReportSummary
    items: list[DecisionReportItem]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================
# APPROVAL REPORT SCHEMAS
# ============================================================

class ApprovalReportItem(BaseModel):
    approval_id: int
    decision_id: int
    decision_title: str
    reviewer_id: int
    reviewer_name: str | None = None
    approval_level: int = 1
    approval_status: str
    assigned_date: datetime
    completed_date: datetime | None = None
    approval_turnaround_time_hours: float | None = None

    model_config = ConfigDict(from_attributes=True)


class ApprovalReportSummary(BaseModel):
    total_approvals: int
    pending_approvals: int
    approved_approvals: int
    rejected_approvals: int
    average_approval_turnaround_time_hours: float | None = None
    approval_completion_rate: float = 0.0


class ApprovalReportResponse(BaseModel):
    summary: ApprovalReportSummary
    items: list[ApprovalReportItem]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================
# TEAM REPORT SCHEMAS
# ============================================================

class TeamApprovalStatistics(BaseModel):
    total_approvals: int
    approved_approvals: int
    rejected_approvals: int
    pending_approvals: int
    average_turnaround_time_hours: float | None = None
    completion_rate: float = 0.0


class TeamReportItem(BaseModel):
    team_name: str
    number_of_members: int
    total_decisions: int
    approved_decisions: int
    rejected_decisions: int
    pending_decisions: int
    team_approval_statistics: TeamApprovalStatistics


class TeamReportSummary(BaseModel):
    total_teams: int
    total_members: int
    total_decisions: int
    total_approvals: int


class TeamReportResponse(BaseModel):
    summary: TeamReportSummary
    items: list[TeamReportItem]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================
# AUDIT REPORT SCHEMAS
# ============================================================

class AuditReportItem(BaseModel):
    audit_id: int
    user_id: int
    user_name: str | None = None
    user_email: str | None = None
    action: str
    entity_type: str
    entity_id: int | None = None
    description: str
    timestamp: datetime
    ip_address: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AuditReportSummary(BaseModel):
    total_audit_records: int
    actions_breakdown: dict[str, int] = {}
    entity_types_breakdown: dict[str, int] = {}


class AuditReportResponse(BaseModel):
    summary: AuditReportSummary
    items: list[AuditReportItem]
    total: int
    page: int
    page_size: int
    total_pages: int
