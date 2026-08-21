from datetime import datetime

from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(
        from_attributes=True
    )