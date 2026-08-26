from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DecisionTagAssign(BaseModel):
    tag_ids: List[int]


class DecisionTagsResponse(BaseModel):
    decision_id: int
    tags: List[TagResponse]
