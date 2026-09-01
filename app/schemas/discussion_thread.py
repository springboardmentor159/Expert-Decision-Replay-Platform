from datetime import datetime

from pydantic import BaseModel, Field


class DiscussionThreadCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)


class DiscussionThreadUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    description: str | None = Field(default=None, min_length=1)


class DiscussionThreadResponse(BaseModel):
    id: int
    decision_id: int
    created_by: int
    title: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True