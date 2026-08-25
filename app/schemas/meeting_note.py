from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class MeetingNoteCreate(BaseModel):
    title: str
    content: str
    meeting_date: date


class MeetingNoteUpdate(BaseModel):
    title: str
    content: str
    meeting_date: date


class MeetingNoteResponse(BaseModel):
    id: int
    decision_id: int
    created_by: int
    title: str
    content: str
    meeting_date: date
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)