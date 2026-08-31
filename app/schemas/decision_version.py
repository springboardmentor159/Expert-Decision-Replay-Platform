from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class DecisionVersionResponse(BaseModel):
    id: int
    decision_id: int
    version_number: int
    title: str
    problem_statement: str
    category: str
    status: str
    rationale: Optional[str] = None
    created_by: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DecisionVersionListItem(BaseModel):
    version_number: int
    created_by: int
    created_at: datetime
    title: Optional[str] = None
    status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
