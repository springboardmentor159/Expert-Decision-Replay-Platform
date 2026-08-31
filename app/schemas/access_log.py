from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class AccessLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    resource_type: str
    resource_id: Optional[int] = None
    action: str
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedAccessLogResponse(BaseModel):
    items: List[AccessLogResponse]
    total: int
    page: int
    page_size: int
