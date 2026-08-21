from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.comment import CommentResponse


class ThreadCreate(BaseModel):
    title: str
    description: Optional[str] = None


class ThreadUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class ThreadResponse(BaseModel):
    id: int
    decision_id: int
    created_by: int
    title: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ThreadDetailResponse(ThreadResponse):
    comments: List[CommentResponse] = []
