from datetime import datetime

from pydantic import BaseModel


class CommentCreate(BaseModel):
    content: str


class CommentUpdate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    decision_id: int
    user_id: int
    thread_id: int | None
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }