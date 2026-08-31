from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class AccessLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    resource_type: str
    resource_id: Optional[int] = None
    action: str
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedAccessLogsResponse(BaseModel):
    items: List[AccessLogResponse]
    page: int
    page_size: int
    total: int
