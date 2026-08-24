from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


# CREATE THREAD
class DiscussionThreadCreate(BaseModel):
    title: str
    description: Optional[str] = None


# UPDATE THREAD
class DiscussionThreadUpdate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = None


# RESPONSE
class DiscussionThreadResponse(BaseModel):
    id: int
    decision_id: int
    created_by: int
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)