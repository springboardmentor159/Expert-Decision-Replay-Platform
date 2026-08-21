from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class AlternativeCreate(BaseModel):
    name: str
    description: str
    pros: str
    cons: str
    estimated_cost: float
    feasibility_score: int = Field(ge=1, le=5)
    risk_level: RiskLevel


class AlternativeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    pros: str | None = None
    cons: str | None = None
    estimated_cost: float | None = None
    feasibility_score: int | None = Field(default=None, ge=1, le=5)
    risk_level: RiskLevel | None = None


class AlternativeResponse(BaseModel):
    id: int
    decision_id: int
    name: str
    description: str
    pros: str
    cons: str
    estimated_cost: float
    feasibility_score: int
    risk_level: RiskLevel
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }