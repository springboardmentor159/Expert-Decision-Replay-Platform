from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DecisionReportItem(BaseModel):
    decision_id: int
    title: str
    category: str
    status: str
    created_by: str
    created_date: datetime
    updated_date: datetime
    number_of_alternatives: int
    number_of_approvals: int
    tags: Optional[str] = None


class DecisionReportSummary(BaseModel):
    total: int
    draft: int
    under_review: int
    approved: int
    rejected: int
    archived: int


class DecisionReportResponse(BaseModel):
    data: list[DecisionReportItem]
    summary: DecisionReportSummary
    page: int
    page_size: int
    total_records: int