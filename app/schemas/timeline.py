from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TimelineEvent(BaseModel):
    event_type: str
    description: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)