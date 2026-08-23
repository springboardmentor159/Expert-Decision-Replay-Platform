from datetime import datetime

from pydantic import BaseModel


class DecisionVersionCreate(BaseModel):
    title: str
    description: str
    status: str


class DecisionVersionResponse(BaseModel):
    id: int
    decision_id: int
    created_by: int
    version_number: int
    title: str
    description: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True