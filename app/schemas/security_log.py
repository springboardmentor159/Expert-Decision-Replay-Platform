from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SecurityLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    event_type: str
    description: str
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True