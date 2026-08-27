from pydantic import BaseModel
from datetime import datetime


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


class PaginatedActivities(BaseModel):
    items: list[ActivityResponse]
    page: int
    page_size: int
    total: int
