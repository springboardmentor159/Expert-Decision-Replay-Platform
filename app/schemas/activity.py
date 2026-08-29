from datetime import datetime
from pydantic import BaseModel


class ActivityResponse(BaseModel):
    id: int
    decision_id: int
    activity_type: str
    description: str
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True