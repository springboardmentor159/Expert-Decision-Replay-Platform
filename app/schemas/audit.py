from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: int
    decision_id: int
    user_id: int
    action: str
    entity_type: str
    entity_id: int | None
    description: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class TimelineResponse(BaseModel):
    action: str
    entity_type: str
    entity_id: int | None
    description: str
    user_id: int
    created_at: datetime