from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, Any


# ---------------------------------------------------------------------
# Sprint 12: Reports & Export
#
# These schemas are intentionally separate from the "operational"
# schemas (app.schemas.decision, app.schemas.approval, ...). Reports are
# read-only, aggregated, and often reshape data (e.g. flattening the
# reviewer's name onto the approval row) in ways that don't belong on
# the entities themselves.
# ---------------------------------------------------------------------


# =======================================================================
# Decision Report
# =======================================================================

class DecisionReportItem(BaseModel):
    decision_id: int
    title: str
    category: str
    status: str
    created_by: int
    created_by_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    alternatives_count: int
    approvals_count: int
    tags: list[str] = []

    class Config:
        from_attributes = True


class DecisionReportSummary(BaseModel):
    total_decisions: int
    draft_decisions: int
    under_review: int
    approved_decisions: int
    rejected_decisions: int
    archived_decisions: int


class DecisionReportResponse(BaseModel):
    items: list[DecisionReportItem]
    summary: DecisionReportSummary
    page: int
    page_size: int
    total: int
    generated_at: datetime
    filters_applied: dict[str, Any]


# =======================================================================
# Approval Report
# =======================================================================

class ApprovalReportItem(BaseModel):
    approval_id: int
    decision_id: int
    decision_title: str
    reviewer_id: int
    reviewer_name: Optional[str] = None
    approval_level: int
    approval_status: str
    assigned_date: datetime
    completed_date: Optional[datetime] = None
    turnaround_hours: Optional[float] = None

    class Config:
        from_attributes = True


class ApprovalReportSummary(BaseModel):
    total_approvals: int
    pending_approvals: int
    approved_approvals: int
    rejected_approvals: int
    average_turnaround_hours: Optional[float] = None
    approval_completion_rate: float


class ApprovalReportResponse(BaseModel):
    items: list[ApprovalReportItem]
    summary: ApprovalReportSummary
    page: int
    page_size: int
    total: int
    generated_at: datetime
    filters_applied: dict[str, Any]


# =======================================================================
# Team Report
# =======================================================================

class TeamApprovalStats(BaseModel):
    total_approvals: int
    pending_approvals: int
    approved_approvals: int
    rejected_approvals: int
    approval_completion_rate: float


class TeamReportItem(BaseModel):
    team_name: str
    member_count: int
    total_decisions: int
    approved_decisions: int
    rejected_decisions: int
    pending_decisions: int
    team_approval_stats: TeamApprovalStats


class TeamReportResponse(BaseModel):
    items: list[TeamReportItem]
    page: int
    page_size: int
    total: int
    generated_at: datetime
    filters_applied: dict[str, Any]


# =======================================================================
# Audit Report
# =======================================================================

class AuditReportItem(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str] = None
    action: str
    entity_type: str
    entity_id: int
    description: str
    timestamp: datetime
    ip_address: Optional[str] = None

    class Config:
        from_attributes = True


class AuditReportResponse(BaseModel):
    items: list[AuditReportItem]
    page: int
    page_size: int
    total: int
    generated_at: datetime
    filters_applied: dict[str, Any]
