from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AccessLogResponse(BaseModel):
    id: int
    user_id: int
    resource_type: str
    resource_id: int
    action: str
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True