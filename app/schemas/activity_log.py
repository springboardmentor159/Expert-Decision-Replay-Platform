from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ActivityLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    entity_type: str
    entity_id: int | None
    description: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)