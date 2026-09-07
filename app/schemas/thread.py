from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserResponse


class ThreadCreate(BaseModel):
    title: str


class ThreadUpdate(BaseModel):
    title: str


class ThreadResponse(BaseModel):
    id: int
    decision_id: int
    title: str
    created_by: int
    created_at: datetime
    updated_at: datetime
    user: Optional[UserResponse] = None

    model_config = ConfigDict(
        from_attributes=True
    )
