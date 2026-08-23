from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DiscussionThreadCreate(BaseModel):
    title: str
    description: str | None = None


class DiscussionThreadUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None


class DiscussionThreadResponse(BaseModel):
    id: int
    decision_id: int
    created_by: int
    title: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)