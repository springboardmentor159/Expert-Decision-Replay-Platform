from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AlternativeCreate(BaseModel):
    name: str
    description: str
    pros: str
    cons: str

    estimated_cost: int = Field(
        ge=0
    )

    feasibility_score: int = Field(
        ge=1,
        le=5
    )

    risk_level: Literal[
        "Low",
        "Medium",
        "High",
        "Critical"
    ]


class AlternativeResponse(BaseModel):
    id: int
    decision_id: int
    name: str
    description: str
    pros: str
    cons: str
    estimated_cost: int
    feasibility_score: int
    risk_level: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
