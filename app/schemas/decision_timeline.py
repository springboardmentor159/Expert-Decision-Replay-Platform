from datetime import datetime

from pydantic import BaseModel


class DecisionTimelineResponse(BaseModel):
    id: int
    decision_id: int
    event_type: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True