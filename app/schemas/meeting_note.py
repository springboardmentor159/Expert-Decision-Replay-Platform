from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MeetingNoteBase(BaseModel):
    """Base schema for MeetingNote data"""
    title: str
    content: str
    meeting_date: datetime


class MeetingNoteCreate(MeetingNoteBase):
    """Schema for creating a new meeting note"""
    pass


class MeetingNoteUpdate(BaseModel):
    """Schema for updating a meeting note"""
    title: str | None = None
    content: str | None = None
    meeting_date: datetime | None = None


class MeetingNoteResponse(MeetingNoteBase):
    """Schema for meeting note response"""
    id: int
    decision_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
