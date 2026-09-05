
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AccessLogResponse(BaseModel):
    id: int
    user_id: int
    resource_type: str
    resource_id: int | None = None
    action: str
    ip_address: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AccessLogListResponse(BaseModel):
    items: list[AccessLogResponse]
    page: int
    page_size: int
    total: int
