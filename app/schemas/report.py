from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict


# =============================================================================
# 1. DECISION REPORT SCHEMAS
# =============================================================================

class DecisionReportItem(BaseModel):
    id: int
    title: str
    category: str
    status: str
    created_by: int
    creator_name: Optional[str] = None
    creator_email: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    alternatives_count: int = 0
    approvals_count: int = 0
    tags: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class DecisionReportSummary(BaseModel):
    total_decisions: int = 0
    draft_decisions: int = 0
    under_review_decisions: int = 0
    approved_decisions: int = 0
    rejected_decisions: int = 0
    archived_decisions: int = 0


class DecisionReportResponse(BaseModel):
    items: List[DecisionReportItem]
    summary: DecisionReportSummary
    page: int
    page_size: int
    total: int


# =============================================================================
# 2. APPROVAL REPORT SCHEMAS
# =============================================================================

class ApprovalReportItem(BaseModel):
    id: int
    decision_id: int
    decision_title: Optional[str] = None
    reviewer_id: int
    reviewer_name: Optional[str] = None
    reviewer_email: Optional[str] = None
    approval_level: int = 1
    status: str
    comments: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    turnaround_time_hours: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class ApprovalReportSummary(BaseModel):
    total_approvals: int = 0
    pending_approvals: int = 0
    approved_approvals: int = 0
    rejected_approvals: int = 0
    average_turnaround_time_hours: Optional[float] = None
    completion_rate: float = 0.0


class ApprovalReportResponse(BaseModel):
    items: List[ApprovalReportItem]
    summary: ApprovalReportSummary
    page: int
    page_size: int
    total: int


# =============================================================================
# 3. TEAM REPORT SCHEMAS
# =============================================================================

class TeamApprovalStats(BaseModel):
    total_approvals: int = 0
    approved_approvals: int = 0
    rejected_approvals: int = 0
    pending_approvals: int = 0
    completion_rate: float = 0.0
    average_turnaround_time_hours: Optional[float] = None


class TeamReportItem(BaseModel):
    team_name: str
    member_count: int = 0
    total_decisions: int = 0
    approved_decisions: int = 0
    rejected_decisions: int = 0
    pending_decisions: int = 0
    draft_decisions: int = 0
    under_review_decisions: int = 0
    team_approval_statistics: TeamApprovalStats


class TeamReportSummary(BaseModel):
    total_teams: int = 0
    total_members: int = 0
    total_decisions: int = 0
    approved_decisions: int = 0
    rejected_decisions: int = 0
    pending_decisions: int = 0


class TeamReportResponse(BaseModel):
    items: List[TeamReportItem]
    summary: TeamReportSummary
    page: int
    page_size: int
    total: int


# =============================================================================
# 4. AUDIT REPORT SCHEMAS
# =============================================================================

class AuditReportItem(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    description: str
    created_at: datetime
    ip_address: Optional[str] = None
    request_method: Optional[str] = None
    endpoint: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AuditReportSummary(BaseModel):
    total_audit_logs: int = 0
    actions_breakdown: Dict[str, int] = {}
    entities_breakdown: Dict[str, int] = {}


class AuditReportResponse(BaseModel):
    items: List[AuditReportItem]
    summary: AuditReportSummary
    page: int
    page_size: int
    total: int
