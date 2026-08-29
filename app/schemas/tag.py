from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TagCreate(BaseModel):
    name: str


class TagResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class DecisionTagAssign(BaseModel):
    tag_ids: list[int]