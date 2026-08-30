from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# CREATE MEETING NOTE
class MeetingNoteCreate(BaseModel):
    title: str
    content: str


# UPDATE MEETING NOTE
class MeetingNoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


# RESPONSE
class MeetingNoteResponse(BaseModel):
    id: int
    decision_id: int
    created_by: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True