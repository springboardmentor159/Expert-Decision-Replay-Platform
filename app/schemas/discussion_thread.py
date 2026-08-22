from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class ThreadStatus(str, Enum):
    OPEN = "Open"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


# decision_id and created_by come from the URL / JWT, never the body.
class DiscussionThreadCreate(BaseModel):
    title: str
    description: Optional[str] = None


class DiscussionThreadUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ThreadStatus] = None


class DiscussionThreadResponse(BaseModel):
    id: int
    decision_id: int
    created_by: int
    title: str
    description: Optional[str] = None
    status: ThreadStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
