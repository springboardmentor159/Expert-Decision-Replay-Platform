from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


# ENUMS for filtering
class ReportSortField(str, Enum):
    created_at = "created_at"
    updated_at = "updated_at"
    title = "title"
    approval_date = "approval_date"
    team_name = "team_name"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


# ============ DECISION REPORT ============

class DecisionReportRow(BaseModel):
    """Individual decision report row"""
    decision_id: int
    decision_title: str
    category: str
    status: str
    created_by: str  # User name
    created_date: datetime
    updated_date: datetime
    number_of_alternatives: int
    number_of_approvals: int
    tags: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class DecisionReportSummary(BaseModel):
    """Summary statistics for decision report"""
    total_decisions: int
    draft_decisions: int
    decisions_under_review: int
    approved_decisions: int
    rejected_decisions: int
    archived_decisions: int


class DecisionReportResponse(BaseModel):
    """Complete decision report response"""
    summary: DecisionReportSummary
    data: List[DecisionReportRow]
    page: int
    page_size: int
    total_records: int
    total_pages: int


# ============ APPROVAL REPORT ============

class ApprovalReportRow(BaseModel):
    """Individual approval report row"""
    approval_id: int
    decision_id: int
    decision_title: str
    reviewer: str
    approval_level: int
    approval_status: str
    assigned_date: datetime
    completed_date: Optional[datetime] = None
    approval_turnaround_time_hours: Optional[float] = None  # None if not yet completed

    model_config = ConfigDict(from_attributes=True)


class ApprovalReportSummary(BaseModel):
    """Summary statistics for approval report"""
    total_approvals: int
    pending_approvals: int
    approved_approvals: int
    rejected_approvals: int
    average_approval_turnaround_time_hours: float
    approval_completion_rate: float  # Percentage


class ApprovalReportResponse(BaseModel):
    """Complete approval report response"""
    summary: ApprovalReportSummary
    data: List[ApprovalReportRow]
    page: int
    page_size: int
    total_records: int
    total_pages: int


# ============ TEAM REPORT ============

class TeamDecisionStats(BaseModel):
    """Decision statistics for a team"""
    total_decisions: int
    approved_decisions: int
    rejected_decisions: int
    pending_decisions: int
    draft_decisions: int


class TeamApprovalStats(BaseModel):
    """Approval statistics for a team"""
    total_approvals: int
    pending_approvals: int
    approved_approvals: int
    rejected_approvals: int
    average_turnaround_time_hours: float


class TeamReportRow(BaseModel):
    """Individual team report row"""
    team_name: str
    number_of_members: int
    decision_stats: TeamDecisionStats
    approval_stats: TeamApprovalStats

    model_config = ConfigDict(from_attributes=True)


class TeamReportResponse(BaseModel):
    """Complete team report response"""
    data: List[TeamReportRow]
    page: int
    page_size: int
    total_records: int
    total_pages: int


# ============ AUDIT REPORT ============

class AuditReportRow(BaseModel):
    """Individual audit report row"""
    audit_id: int
    user: str  # User name
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    description: str
    timestamp: datetime
    ip_address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AuditReportResponse(BaseModel):
    """Complete audit report response"""
    data: List[AuditReportRow]
    page: int
    page_size: int
    total_records: int
    total_pages: int


# ============ FILTER MODELS ============

class DecisionReportFilters(BaseModel):
    """Filters for decision report"""
    category: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[int] = None  # User ID
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    tags: Optional[List[str]] = None  # List of tag names
    sort_by: ReportSortField = ReportSortField.created_at
    sort_order: SortOrder = SortOrder.desc
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class ApprovalReportFilters(BaseModel):
    """Filters for approval report"""
    status: Optional[str] = None  # Pending, Approved, Rejected
    reviewer_id: Optional[int] = None
    decision_id: Optional[int] = None
    approval_level: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    sort_by: ReportSortField = ReportSortField.created_at
    sort_order: SortOrder = SortOrder.desc
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class TeamReportFilters(BaseModel):
    """Filters for team report"""
    team_name: Optional[str] = None
    decision_status: Optional[str] = None
    category: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    sort_by: ReportSortField = ReportSortField.team_name
    sort_order: SortOrder = SortOrder.asc
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class AuditReportFilters(BaseModel):
    """Filters for audit report"""
    user_id: Optional[int] = None
    action: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    sort_by: ReportSortField = ReportSortField.created_at
    sort_order: SortOrder = SortOrder.desc
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
