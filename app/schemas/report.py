from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# =========================================================
# DECISION REPORT
# =========================================================

class DecisionReportItem(BaseModel):
    decision_id: int
    title: str
    category: str
    status: str
    created_by: Optional[str] = None
    created_date: datetime
    updated_date: datetime
    number_of_alternatives: int
    number_of_approvals: int
    tags: List[str]


class DecisionReportSummary(BaseModel):
    total_decisions: int
    draft_decisions: int
    under_review_decisions: int
    approved_decisions: int
    rejected_decisions: int
    archived_decisions: int


class DecisionReportResponse(BaseModel):
    page: int
    page_size: int
    total_records: int
    total_pages: int
    sort_by: str
    sort_order: str

    summary: DecisionReportSummary
    data: List[DecisionReportItem]


# =========================================================
# APPROVAL REPORT
# =========================================================

class ApprovalReportItem(BaseModel):
    approval_id: int
    decision_id: int
    decision_title: str
    reviewer: Optional[str] = None
    approval_level: Optional[str] = None
    approval_status: str
    assigned_date: datetime
    completed_date: Optional[datetime] = None
    approval_turnaround_time_hours: Optional[float] = None


class ApprovalReportSummary(BaseModel):
    total_approvals: int
    pending_approvals: int
    approved_approvals: int
    rejected_approvals: int
    average_approval_turnaround_time_hours: Optional[float] = None
    approval_completion_rate: float


class ApprovalReportResponse(BaseModel):
    page: int
    page_size: int
    total_records: int
    total_pages: int
    sort_by: str
    sort_order: str

    summary: ApprovalReportSummary
    data: List[ApprovalReportItem]

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
    average_approval_turnaround_time_hours: Optional[float] = None


class TeamReportResponse(BaseModel):
    page: int
    page_size: int
    total_records: int
    total_pages: int
    sort_by: str
    sort_order: str
    data: List[TeamReportItem]

class AuditReportItem(BaseModel):
    user: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    description: Optional[str] = None
    timestamp: datetime
    ip_address: Optional[str] = None


class AuditReportResponse(BaseModel):
    page: int
    page_size: int
    total_records: int
    total_pages: int
    sort_by: str
    sort_order: str
    data: List[AuditReportItem]