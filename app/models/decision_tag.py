from pydantic import BaseModel
from typing import List


class AssignTagsRequest(BaseModel):
    tag_ids: List[int]