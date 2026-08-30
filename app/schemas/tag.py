from datetime import datetime
from pydantic import BaseModel, Field


# CREATE TAG
class TagCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100
    )


# TAG RESPONSE
class TagResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


# ASSIGN TAGS TO A DECISION
class AssignTags(BaseModel):
    tag_ids: list[int]