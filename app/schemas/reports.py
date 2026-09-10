from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ============================================================
# DECISION REPORT
# ============================================================

class DecisionReportItem(BaseModel):
    decision_id: int
    title: str
    category: str
    status: str
    created_by: int
    created_date: datetime
    updated_date: Optional[datetime] = None
    alternatives_count: int
    approvals_count: int
    tags: list[str] = []

    model_config = ConfigDict(from_attributes=True)


class DecisionReportSummary(BaseModel):
    total_decisions: int
    draft_decisions: int
    under_review_decisions: int
    approved_decisions: int
    rejected_decisions: int
    archived_decisions: int


class DecisionReportResponse(BaseModel):
    items: list[DecisionReportItem]
    summary: DecisionReportSummary
    page: int
    page_size: int
    total: int


# ============================================================
# APPROVAL REPORT
# ============================================================

class ApprovalReportItem(BaseModel):
    approval_id: int
    decision_id: int
    decision_title: str
    reviewer_id: int
    approval_level: int
    status: str
    assigned_date: datetime
    completed_date: Optional[datetime] = None
    turnaround_days: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class ApprovalReportSummary(BaseModel):
    total_approvals: int
    pending_approvals: int
    approved_approvals: int
    rejected_approvals: int
    average_turnaround_days: Optional[float] = None
    completion_rate: float


class ApprovalReportResponse(BaseModel):
    items: list[ApprovalReportItem]
    summary: ApprovalReportSummary
    page: int
    page_size: int
    total: int

# ============================================================
# TEAM REPORT
# ============================================================

class TeamReportItem(BaseModel):
    team_name: str
    members: int
    total_decisions: int
    approved_decisions: int
    rejected_decisions: int
    pending_decisions: int
    approval_rate: float

    model_config = ConfigDict(from_attributes=True)


class TeamReportSummary(BaseModel):
    total_teams: int
    total_members: int
    total_decisions: int
    total_approved: int
    total_rejected: int
    total_pending: int


class TeamReportResponse(BaseModel):
    items: list[TeamReportItem]
    summary: TeamReportSummary
    page: int
    page_size: int
    total: int
# ============================================================
# AUDIT REPORT
# ============================================================

class AuditReportItem(BaseModel):
    audit_id: int
    user_id: Optional[int] = None
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    description: str
    timestamp: datetime
    ip_address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AuditReportSummary(BaseModel):
    total_audit_logs: int
    create_actions: int
    update_actions: int
    delete_actions: int
    approve_actions: int
    reject_actions: int
    access_actions: int
    login_actions: int
    logout_actions: int
    submit_actions: int
    archive_actions: int


class AuditReportResponse(BaseModel):
    items: list[AuditReportItem]
    summary: AuditReportSummary
    page: int
    page_size: int
    total: int