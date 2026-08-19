from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DecisionCreate(BaseModel):
    title: str
    problem_statement: str
    category: str


class DecisionResponse(BaseModel):
    id: int
    title: str
    problem_statement: str
    category: str
    status: str
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
