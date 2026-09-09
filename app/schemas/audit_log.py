from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.audit_action import AuditAction
from app.models.audit_entity import AuditEntityType


class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: AuditAction
    entity_type: AuditEntityType
    entity_id: int
    description: str
    ip_address: Optional[str] = None
    old_value: Optional[dict] = None
    new_value: Optional[dict] = None
    request_method: Optional[str] = None
    endpoint: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True