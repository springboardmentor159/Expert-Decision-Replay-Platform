from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# =============================================================================
# 1. DECISION REPORTS
# =============================================================================

class DecisionReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    decision_id: int
    title: str
    category: str
    status: str
    created_by: int
    created_by_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    number_of_alternatives: int = 0
    number_of_approvals: int = 0
    tags: List[str] = []


class DecisionReportSummary(BaseModel):
    total_decisions: int = 0
    draft_decisions: int = 0
    decisions_under_review: int = 0
    approved_decisions: int = 0
    rejected_decisions: int = 0
    archived_decisions: int = 0


class DecisionReportResponse(BaseModel):
    items: List[DecisionReportItem]
    summary: DecisionReportSummary
    total: int
    page: int
    page_size: int
    total_pages: int


# =============================================================================
# 2. APPROVAL REPORTS
# =============================================================================

class ApprovalReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    approval_id: int
    decision_id: int
    decision_title: str
    reviewer_id: int
    reviewer_name: Optional[str] = None
    reviewer_email: Optional[str] = None
    approval_level: int = 1
    approval_status: str  # Pending, Approved, Rejected
    assigned_date: datetime
    completed_date: Optional[datetime] = None
    turnaround_time_hours: Optional[float] = None


class ApprovalReportSummary(BaseModel):
    total_approvals: int = 0
    pending_approvals: int = 0
    approved_approvals: int = 0
    rejected_approvals: int = 0
    average_turnaround_time_hours: Optional[float] = None
    approval_completion_rate: float = 0.0


class ApprovalReportResponse(BaseModel):
    items: List[ApprovalReportItem]
    summary: ApprovalReportSummary
    total: int
    page: int
    page_size: int
    total_pages: int


# =============================================================================
# 3. TEAM REPORTS
# =============================================================================

class TeamApprovalStats(BaseModel):
    total_approvals: int = 0
    approved_approvals: int = 0
    rejected_approvals: int = 0
    pending_approvals: int = 0
    average_turnaround_time_hours: Optional[float] = None


class TeamReportItem(BaseModel):
    team_name: str
    number_of_members: int = 0
    total_decisions: int = 0
    approved_decisions: int = 0
    rejected_decisions: int = 0
    pending_decisions: int = 0  # under review
    team_approval_statistics: TeamApprovalStats


class TeamReportSummary(BaseModel):
    total_teams: int = 0
    total_members: int = 0
    total_decisions: int = 0
    total_approvals: int = 0


class TeamReportResponse(BaseModel):
    items: List[TeamReportItem]
    summary: TeamReportSummary
    total: int
    page: int
    page_size: int
    total_pages: int


# =============================================================================
# 4. AUDIT REPORTS
# =============================================================================

class AuditReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    description: str
    timestamp: datetime
    ip_address: Optional[str] = None
    request_method: Optional[str] = None
    endpoint: Optional[str] = None


class AuditReportSummary(BaseModel):
    total_events: int = 0
    action_breakdown: Dict[str, int] = {}
    entity_breakdown: Dict[str, int] = {}


class AuditReportResponse(BaseModel):
    items: List[AuditReportItem]
    summary: AuditReportSummary
    total: int
    page: int
    page_size: int
    total_pages: int
