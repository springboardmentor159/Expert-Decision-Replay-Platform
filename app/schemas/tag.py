from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict


class TagCreate(BaseModel):
    name: str


class TagResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TagAssignment(BaseModel):
    tag_ids: List[int]