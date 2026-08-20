from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# =========================
# CREATE ALTERNATIVE
# =========================

class AlternativeCreate(BaseModel):
    name: str
    description: str
    pros: str
    cons: str
    estimated_cost: float
    feasibility_score: int = Field(
        ge=1,
        le=5,
        description="Feasibility score must be between 1 and 5"
    )
    risk_level: str = Field(
        pattern="^(Low|Medium|High|Critical)$",
        description="Risk level must be Low, Medium, High, or Critical"
    )


# =========================
# UPDATE ALTERNATIVE
# =========================

class AlternativeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    pros: Optional[str] = None
    cons: Optional[str] = None
    estimated_cost: Optional[float] = None

    feasibility_score: Optional[int] = Field(
        default=None,
        ge=1,
        le=5,
        description="Feasibility score must be between 1 and 5"
    )

    risk_level: Optional[str] = Field(
        default=None,
        pattern="^(Low|Medium|High|Critical)$",
        description="Risk level must be Low, Medium, High, or Critical"
    )


# =========================
# RESPONSE
# =========================

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