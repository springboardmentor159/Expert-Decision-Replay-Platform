from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CommentCreate(BaseModel):
    content: str


class CommentUpdate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    decision_id: int
    user_id: int
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True