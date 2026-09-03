from datetime import datetime

from pydantic import BaseModel


class ActivityResponse(BaseModel):
    id: int
    user_id: int
    action: str
    entity_type: str
    entity_id: int
    description: str
    created_at: datetime

    class Config:
        from_attributes = True