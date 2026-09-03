from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class TagResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DecisionTagAssignment(BaseModel):
    tag_ids: list[int] = Field(default_factory=list)