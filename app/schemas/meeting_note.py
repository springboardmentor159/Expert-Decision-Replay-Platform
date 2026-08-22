from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# decision_id and created_by come from the URL / JWT, never the body.
class MeetingNoteCreate(BaseModel):
    title: str
    content: str
    meeting_date: datetime


class MeetingNoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    meeting_date: Optional[datetime] = None


class MeetingNoteResponse(BaseModel):
    id: int
    decision_id: int
    created_by: int
    title: str
    content: str
    meeting_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
