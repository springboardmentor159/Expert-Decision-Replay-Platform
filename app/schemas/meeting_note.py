from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MeetingNoteCreate(BaseModel):
    title: str
    content: str
    meeting_date: Optional[datetime] = None


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

    model_config = ConfigDict(from_attributes=True)
