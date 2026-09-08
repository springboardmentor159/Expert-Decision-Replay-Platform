from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


# --- Decisions Report ---

class DecisionReportItem(BaseModel):
    id: int
    title: str
    category: str
    status: str
    creator: str
    created_at: datetime
    updated_at: datetime
    alternative_count: int
    approval_count: int
    tags: List[str]

    model_config = ConfigDict(from_attributes=True)


class DecisionReportSummary(BaseModel):
    total: int
    draft: int
    under_review: int
    approved: int
    rejected: int
    archived: int


class DecisionReportResponse(BaseModel):
    items: List[DecisionReportItem]
    summary: DecisionReportSummary
    total: int
    page: int
    page_size: int
    pages: int


# --- Approvals Report ---

class ApprovalReportItem(BaseModel):
    id: int
    decision_id: int
    decision_title: str
    reviewer: str
    level: Optional[str] = None
    status: str
    assigned_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    turnaround_time_hours: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class ApprovalReportSummary(BaseModel):
    total: int
    pending: int
    approved: int
    rejected: int
    average_turnaround_hours: Optional[float] = None
    completion_rate: float


class ApprovalReportResponse(BaseModel):
    items: List[ApprovalReportItem]
    summary: ApprovalReportSummary
    total: int
    page: int
    page_size: int
    pages: int


# --- Teams Report ---

class TeamApprovalStats(BaseModel):
    pending: int
    approved: int
    rejected: int


class TeamReportItem(BaseModel):
    team: str
    member_count: int
    decision_count: int
    approval_stats: TeamApprovalStats


class TeamReportResponse(BaseModel):
    items: List[TeamReportItem]
    total: int
    page: int
    page_size: int
    pages: int


# --- Audit Report ---

class AuditReportItem(BaseModel):
    id: int
    user: str
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    description: Optional[str] = None
    timestamp: datetime
    ip_address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AuditReportResponse(BaseModel):
    items: List[AuditReportItem]
    total: int
    page: int
    page_size: int
    pages: int
