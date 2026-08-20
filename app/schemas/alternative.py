from datetime import datetime

from pydantic import BaseModel, Field


class AlternativeCreate(BaseModel):
    name: str
    description: str
    pros: str
    cons: str
    estimated_cost: float
    feasibility_score: int = Field(ge=1, le=5)
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

    class Config:
        from_attributes = True