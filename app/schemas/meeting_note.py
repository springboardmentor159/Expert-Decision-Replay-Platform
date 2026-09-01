from datetime import date, datetime

from pydantic import BaseModel, Field


class MeetingNoteCreate(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    meeting_date: date


class MeetingNoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    content: str | None = Field(default=None, min_length=1)
    meeting_date: date | None = None


class MeetingNoteResponse(BaseModel):
    id: int
    decision_id: int
    created_by: int
    title: str
    content: str
    meeting_date: date
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True