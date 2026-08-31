from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class SecurityLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    event_type: str
    description: str
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedSecurityLogResponse(BaseModel):
    items: List[SecurityLogResponse]
    total: int
    page: int
    page_size: int
