from datetime import datetime

from pydantic import BaseModel


class TagCreate(BaseModel):
    name: str


class TagResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
class DecisionTagsUpdate(BaseModel):
    tag_ids: list[int]    