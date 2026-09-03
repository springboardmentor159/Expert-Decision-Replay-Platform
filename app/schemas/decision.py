from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DecisionCreate(BaseModel):
    title: str
    problem_statement: str
    category: str
    tags: Optional[str] = None


class DecisionUpdate(BaseModel):
    title: str
    problem_statement: str
    category: str
    tags: Optional[str] = None


class DecisionStatusUpdate(BaseModel):
    status: str


class DecisionResponse(BaseModel):
    id: int
    title: str
    problem_statement: str
    category: str
    status: str
    tags: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True