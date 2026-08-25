from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AlternativeCreate(BaseModel):
    decision_id: int
    name: str
    description: str
    pros: str
    cons: str
    estimated_cost: float
    feasibility_score: int
    risk_level: str


class AlternativeResponse(BaseModel):
    id: int
    decision_id: int
    name: str
    description: str
    pros: str
    cons: str
    estimated_cost: float
    feasibility_score: int
    risk_level: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)