from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# Only the content is ever accepted from the client.
# decision_id, thread_id, user_id, id, created_at, updated_at
# are always controlled by the backend.
class CommentCreate(BaseModel):
    content: str


# The only field a client may update on a comment.
class CommentUpdate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    decision_id: int
    thread_id: Optional[int] = None
    user_id: int
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
