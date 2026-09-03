from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ApprovalReportItem(BaseModel):
    approval_id: int
    decision_id: int
    decision_title: str
    reviewer: str
    approval_level: int
    approval_status: str
    assigned_date: datetime
    completed_date: Optional[datetime] = None
    approval_turnaround_time: Optional[float] = None


class ApprovalReportStats(BaseModel):
    total: int
    pending: int
    approved: int
    rejected: int
    average_turnaround: Optional[float] = None
    completion_rate: float


class ApprovalReportResponse(BaseModel):
    data: list[ApprovalReportItem]
    stats: ApprovalReportStats
    page: int
    page_size: int
    total_records: int