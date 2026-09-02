from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CommentBase(BaseModel):
    """Base schema for Comment data"""
    content: str


class CommentCreate(CommentBase):
    """Schema for creating a new comment"""
    pass


class CommentUpdate(BaseModel):
    """Schema for updating a comment"""
    content: str


class CommentResponse(CommentBase):
    """Schema for comment response"""
    id: int
    decision_id: int
    user_id: int
    thread_id: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
