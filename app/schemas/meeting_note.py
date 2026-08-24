from datetime import datetime

from pydantic import BaseModel


class MeetingNoteCreate(BaseModel):
    title: str
    content: str
    meeting_date: datetime


class MeetingNoteUpdate(BaseModel):
    title: str
    content: str
    meeting_date: datetime


class MeetingNoteResponse(BaseModel):
    id: int
    decision_id: int
    created_by: int
    title: str
    content: str
    meeting_date: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }