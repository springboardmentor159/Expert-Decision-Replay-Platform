from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AlternativeCreate(BaseModel):
    name: str
    description: str
    pros: str
    cons: str

    estimated_cost: int = Field(ge=0)

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


class AlternativeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    pros: str | None = None
    cons: str | None = None

    estimated_cost: int | None = Field(
        default=None,
        ge=0
    )

    feasibility_score: int | None = Field(
        default=None,
        ge=1,
        le=5
    )

    risk_level: Literal[
        "Low",
        "Medium",
        "High",
        "Critical"
    ] | None = None


class AlternativeResponse(BaseModel):
    id: int
    decision_id: int

    name: str
    description: str
    pros: str
    cons: str

    estimated_cost: int
    feasibility_score: int
    risk_level: Literal[
        "Low",
        "Medium",
        "High",
        "Critical"
    ]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
# =========================================================
# ALTERNATIVE COMPARISON
# =========================================================

class AlternativeComparison(BaseModel):
    alternative_id: int
    name: str
    estimated_cost: int
    feasibility_score: int
    risk_level: Literal[
        "Low",
        "Medium",
        "High",
        "Critical"
    ]


class AlternativeComparisonResponse(BaseModel):
    decision_id: int
    alternatives: list[AlternativeComparison]