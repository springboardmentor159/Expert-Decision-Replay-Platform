from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DiscussionThreadCreate(BaseModel):
    title: str
    description: str


class DiscussionThreadUpdate(BaseModel):
    title: str
    description: str
    status: str


class DiscussionThreadResponse(BaseModel):
    id: int
    decision_id: int
    created_by: int
    title: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)