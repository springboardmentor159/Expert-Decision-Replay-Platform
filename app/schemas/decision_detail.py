from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.decision import DecisionStatus

from app.schemas.alternative import AlternativeResponse
from app.schemas.comment import CommentResponse
from app.schemas.meeting_note import MeetingNoteResponse
from app.schemas.tag import TagResponse
from app.schemas.thread import (
    ThreadResponse as DiscussionThreadResponse
)


class DecisionDetailResponse(BaseModel):
    id: int
    title: str
    problem_statement: str
    rationale: str | None
    category: str
    status: DecisionStatus
    created_by: int
    created_at: datetime
    updated_at: datetime

    alternatives: list[AlternativeResponse]
    comments: list[CommentResponse]
    discussion_threads: list[DiscussionThreadResponse]
    meeting_notes: list[MeetingNoteResponse]
    tags: list[TagResponse]

    model_config = ConfigDict(
        from_attributes=True
    )