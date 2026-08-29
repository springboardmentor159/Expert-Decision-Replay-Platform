from datetime import datetime

from pydantic import BaseModel, ConfigDict
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)

from sqlalchemy import or_
from sqlalchemy.orm import Session

class TagAssignment(BaseModel):
    tag_ids: list[int]


class DecisionListItem(BaseModel):
    id: int
    title: str
    category: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DecisionListResponse(BaseModel):
    items: list[DecisionListItem]
    page: int
    page_size: int
    total: int