from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class DecisionCreate(BaseModel):
    title: str
    problem_statement: str
    category: str
    rationale: Optional[str] = None


class DecisionUpdate(BaseModel):
    title: Optional[str] = None
    problem_statement: Optional[str] = None
    category: Optional[str] = None
    rationale: Optional[str] = None


class DecisionResponse(BaseModel):
    id: int
    title: str
    problem_statement: str
    category: str
    status: str
    rationale: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DecisionListItem(BaseModel):
    id: int
    title: str
    category: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DecisionListResponse(BaseModel):
    items: List[DecisionListItem]
    page: int
    page_size: int
    total: int