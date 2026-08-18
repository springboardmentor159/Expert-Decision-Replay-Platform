from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.alternative import RiskLevel


class AlternativeCreate(BaseModel):
    name: str
    description: str
    pros: str
    cons: str
    estimated_cost: Decimal
    feasibility_score: int = Field(
        ge=1,
        le=5
    )
    risk_level: RiskLevel


class AlternativeUpdate(BaseModel):
    name: str
    description: str
    pros: str
    cons: str
    estimated_cost: Decimal
    feasibility_score: int = Field(
        ge=1,
        le=5
    )
    risk_level: RiskLevel


class AlternativeResponse(BaseModel):
    id: int
    decision_id: int
    name: str
    description: str
    pros: str
    cons: str
    estimated_cost: Decimal
    feasibility_score: int
    risk_level: RiskLevel
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )