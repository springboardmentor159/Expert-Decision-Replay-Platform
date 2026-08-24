from datetime import datetime

from pydantic import BaseModel


class ThreadCreate(BaseModel):
    title: str
    description: str


class ThreadUpdate(BaseModel):
    title: str
    description: str
    status: str


class ThreadResponse(BaseModel):
    id: int
    decision_id: int
    created_by: int
    title: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }