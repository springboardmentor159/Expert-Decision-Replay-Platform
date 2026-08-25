from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MeetingNoteCreate(BaseModel):
    title: str
    content: str
    meeting_date: datetime


class MeetingNoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    meeting_date: datetime | None = None


class MeetingNoteResponse(BaseModel):
    id: int
    decision_id: int
    created_by: int
    title: str
    content: str
    meeting_date: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
