from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AccessLogCreate(BaseModel):
    method: str
    path: str
    status_code: int
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    response_time_ms: Optional[int] = None


class AccessLogResponse(BaseModel):
    id: int
    method: str
    path: str
    status_code: int
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    response_time_ms: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
