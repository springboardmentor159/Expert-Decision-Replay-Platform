from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class ActivityLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    description: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedActivityLogResponse(BaseModel):
    items: List[ActivityLogResponse]
    total: int
    page: int
    page_size: int
