from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ThreadStatus(str, Enum):
    OPEN = "Open"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


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