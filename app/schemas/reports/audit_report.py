from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AuditReportItem(BaseModel):
    user: str
    action: str
    entity_type: str
    entity_id: int
    description: str
    timestamp: datetime
    ip_address: Optional[str] = None


class AuditReportResponse(BaseModel):
    data: list[AuditReportItem]
    page: int
    page_size: int
    total_records: int