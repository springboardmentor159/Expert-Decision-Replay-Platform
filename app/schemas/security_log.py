from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class SecurityLogBase(BaseModel):
    user_id: Optional[int] = None
    event_type: str
    description: Optional[str] = None
    ip_address: Optional[str] = None


class SecurityLogCreate(SecurityLogBase):
    pass


class SecurityLogResponse(SecurityLogBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SecurityLogListResponse(BaseModel):
    items: List[SecurityLogResponse]
    page: int
    page_size: int
    total: int