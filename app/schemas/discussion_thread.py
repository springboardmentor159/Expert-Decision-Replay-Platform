from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ThreadCreate(BaseModel):
    title: str
    description: str | None = None


class ThreadUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None


class ThreadResponse(BaseModel):
    id: int
    decision_id: int
    created_by: int
    title: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
