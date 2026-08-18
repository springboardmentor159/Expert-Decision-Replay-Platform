from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AlternativeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    pros: Optional[str] = None
    cons: Optional[str] = None
    estimated_cost: Optional[int] = None
    feasibility_score: Optional[int] = None
    risk_level: Optional[str] = None


class AlternativeResponse(BaseModel):
    id: int
    decision_id: int
    name: str
    description: Optional[str]
    pros: Optional[str]
    cons: Optional[str]
    estimated_cost: Optional[int]
    feasibility_score: Optional[int]
    risk_level: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)