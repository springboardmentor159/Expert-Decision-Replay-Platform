from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import SecurityEventType


class SecurityLogCreate(BaseModel):
    event_type: SecurityEventType
    user_id: Optional[int] = None
    description: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class SecurityLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    event_type: str
    description: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
