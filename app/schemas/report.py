from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ReportPagination(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class DecisionReportRow(BaseModel):
    decision_id: int
    title: str
    category: str
    status: str
    created_by: Optional[str] = None
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    number_of_alternatives: int
    number_of_approvals: int
    tags: list[str] = []


class DecisionReportSummary(BaseModel):
    total_decisions: int
    draft: int
    under_review: int
    approved: int
    rejected: int
    archived: int


class DecisionReportResponse(BaseModel):
    summary: DecisionReportSummary
    data: list[DecisionReportRow]
    pagination: ReportPagination


class ApprovalReportRow(BaseModel):
    approval_id: int
    decision_id: int
    decision_title: str
    reviewer: Optional[str] = None
    approval_level: int
    approval_status: str
    assigned_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    approval_turnaround_time: Optional[str] = None


class ApprovalReportStats(BaseModel):
    total_approvals: int
    pending: int
    approved: int
    rejected: int
    average_approval_turnaround: Optional[str] = None
    completion_rate: float


class ApprovalReportResponse(BaseModel):
    stats: ApprovalReportStats
    data: list[ApprovalReportRow]
    pagination: ReportPagination


class TeamReportRow(BaseModel):
    team_name: str
    number_of_members: int
    total_decisions: int
    approved_decisions: int
    rejected_decisions: int
    pending_decisions: int
    team_approval_statistics: dict[str, Any]


class TeamReportResponse(BaseModel):
    data: list[TeamReportRow]
    pagination: ReportPagination


class AuditReportRow(BaseModel):
    user: Optional[str] = None
    action: str
    entity_type: str
    entity_id: int
    description: str
    timestamp: Optional[datetime] = None
    ip_address: Optional[str] = None


class AuditReportResponse(BaseModel):
    data: list[AuditReportRow]
    pagination: ReportPagination