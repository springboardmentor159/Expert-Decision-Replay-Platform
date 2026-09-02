from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class ThreadStatus(str, Enum):
    """Enum for Discussion Thread status values"""
    Open = "Open"
    Resolved = "Resolved"
    Closed = "Closed"


class DiscussionThreadBase(BaseModel):
    """Base schema for DiscussionThread data"""
    title: str
    description: str


class DiscussionThreadCreate(DiscussionThreadBase):
    """Schema for creating a new discussion thread"""
    pass


class DiscussionThreadUpdate(BaseModel):
    """Schema for updating a discussion thread"""
    title: str | None = None
    description: str | None = None
    status: ThreadStatus | None = None


class DiscussionThreadResponse(DiscussionThreadBase):
    """Schema for discussion thread response"""
    id: int
    decision_id: int
    created_by: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
