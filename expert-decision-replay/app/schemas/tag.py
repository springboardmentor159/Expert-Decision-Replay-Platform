from datetime import datetime

from pydantic import BaseModel, ConfigDict


# =========================================================
# CREATE TAG
# =========================================================

class TagCreate(BaseModel):
    name: str


# =========================================================
# TAG RESPONSE
# =========================================================

class TagResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# ASSIGN TAGS TO DECISION
# =========================================================

class AssignTagsRequest(BaseModel):
    tag_ids: list[int]