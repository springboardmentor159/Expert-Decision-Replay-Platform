from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.alternative_enums import RiskLevel


class AlternativeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    pros: Optional[str] = None
    cons: Optional[str] = None
    estimated_cost: Optional[int] = None
    feasibility_score: int = Field(..., ge=1, le=5)
    risk_level: RiskLevel


class AlternativeUpdate(BaseModel):
    name: str
    description: Optional[str] = None
    pros: Optional[str] = None
    cons: Optional[str] = None
    estimated_cost: Optional[int] = None
    feasibility_score: int = Field(..., ge=1, le=5)
    risk_level: RiskLevel


class AlternativeResponse(BaseModel):
    id: int
    decision_id: int
    name: str
    description: Optional[str] = None
    pros: Optional[str] = None
    cons: Optional[str] = None
    estimated_cost: Optional[int] = None
    feasibility_score: int
    risk_level: RiskLevel
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlternativeCompareItem(BaseModel):
    name: str
    estimated_cost: Optional[int] = None
    feasibility_score: int
    risk_level: RiskLevel

    class Config:
        from_attributes = True


class AlternativeCompareResponse(BaseModel):
    decision_id: int
    alternatives: list[AlternativeCompareItem]