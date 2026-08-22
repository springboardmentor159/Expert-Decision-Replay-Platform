from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


# Fields required to create an alternative.
# decision_id comes from the URL, not the body.
# id, created_at, updated_at are backend-controlled.
class AlternativeCreate(BaseModel):
    name: str
    description: str
    pros: str
    cons: str
    estimated_cost: float
    feasibility_score: int = Field(..., ge=1, le=5)
    risk_level: RiskLevel


# Fields the client is allowed to update.
# id, decision_id, created_at are intentionally NOT here.
class AlternativeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    pros: Optional[str] = None
    cons: Optional[str] = None
    estimated_cost: Optional[float] = None
    feasibility_score: Optional[int] = Field(default=None, ge=1, le=5)
    risk_level: Optional[RiskLevel] = None


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

    class Config:
        from_attributes = True


# Slim shape used only by the comparison endpoint
class AlternativeCompareItem(BaseModel):
    name: str
    estimated_cost: float
    feasibility_score: int
    risk_level: RiskLevel

    class Config:
        from_attributes = True


class AlternativeCompareResponse(BaseModel):
    decision_id: int
    alternatives: List[AlternativeCompareItem]