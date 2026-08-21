from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class AlternativeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str
    pros: str
    cons: str

    estimated_cost: int = Field(..., ge=0)

    feasibility_score: int = Field(
        ...,
        ge=1,
        le=5,
        description="1=Very difficult, 2=Difficult, 3=Moderate, 4=Good, 5=Excellent"
    )

    risk_level: RiskLevel


class AlternativeUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    pros: str | None = None
    cons: str | None = None

    estimated_cost: int | None = Field(None, ge=0)

    feasibility_score: int | None = Field(
        None,
        ge=1,
        le=5
    )

    risk_level: RiskLevel | None = None


class AlternativeResponse(BaseModel):
    id: int
    decision_id: int

    name: str
    description: str
    pros: str
    cons: str

    estimated_cost: int
    feasibility_score: int
    risk_level: RiskLevel

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)