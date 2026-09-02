from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: int
    decision_id: int | None
    user_id: int | None
    action: str
    entity_type: str
    entity_id: int
    description: str
    ip_address: str | None
    old_value: dict[str, Any] | None
    new_value: dict[str, Any] | None
    request_method: str | None
    endpoint: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)