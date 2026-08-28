from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ActivityLogResponse(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str] = None
    action: str
    entity_type: str
    entity_id: int
    description: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedActivitiesResponse(BaseModel):
    items: List[ActivityLogResponse]
    page: int
    page_size: int
    total: int
