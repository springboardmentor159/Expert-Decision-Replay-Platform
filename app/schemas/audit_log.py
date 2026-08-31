from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    description: str
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    ip_address: Optional[str] = None
    request_method: Optional[str] = None
    endpoint: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedAuditLogResponse(BaseModel):
    items: List[AuditLogResponse]
    total: int
    page: int
    page_size: int
