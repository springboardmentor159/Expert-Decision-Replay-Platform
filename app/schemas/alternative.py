from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class AlternativeBase(BaseModel):
    name: str
    description: str
    pros: str
    cons: str
    estimated_cost: float = Field(..., ge=0, description="Estimated cost of the alternative")
    feasibility_score: int = Field(
        ...,
        ge=1,
        le=5,
        description="Feasibility score from 1 (Very difficult) to 5 (Very feasible)"
    )
    risk_level: RiskLevel


class AlternativeCreate(AlternativeBase):
    pass


class AlternativeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    pros: Optional[str] = None
    cons: Optional[str] = None
    estimated_cost: Optional[float] = Field(None, ge=0)
    feasibility_score: Optional[int] = Field(None, ge=1, le=5)
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
    risk_level: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlternativeCompareItem(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    pros: Optional[str] = None
    cons: Optional[str] = None
    estimated_cost: float
    feasibility_score: int
    risk_level: str

    model_config = ConfigDict(from_attributes=True)


class AlternativeComparisonResponse(BaseModel):
    decision_id: int
    alternatives: List[AlternativeCompareItem]

    model_config = ConfigDict(from_attributes=True)
