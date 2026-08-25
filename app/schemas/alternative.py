from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import RiskLevel


class AlternativeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    pros: Optional[str] = None
    cons: Optional[str] = None
    estimated_cost: Optional[int] = None
    feasibility_score: Optional[int] = Field(default=None, ge=1, le=5)
    risk_level: Optional[RiskLevel] = None


class AlternativeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    pros: Optional[str] = None
    cons: Optional[str] = None
    estimated_cost: Optional[int] = None
    feasibility_score: Optional[int] = Field(default=None, ge=1, le=5)
    risk_level: Optional[RiskLevel] = None


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


class AlternativeCompareItem(BaseModel):
    name: str
    estimated_cost: Optional[int] = None
    feasibility_score: Optional[int] = None
    risk_level: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AlternativeCompareResponse(BaseModel):
    decision_id: int
    alternatives: List[AlternativeCompareItem]