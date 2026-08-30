from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ExpertEvaluationCreate(BaseModel):
    alternative_id: int

    feasibility_score: int = Field(
        ge=1,
        le=5
    )

    risk_score: int = Field(
        ge=1,
        le=5
    )

    cost_score: int = Field(
        ge=1,
        le=5
    )

    comments: Optional[str] = None


class ExpertEvaluationUpdate(BaseModel):
    feasibility_score: Optional[int] = Field(
        default=None,
        ge=1,
        le=5
    )

    risk_score: Optional[int] = Field(
        default=None,
        ge=1,
        le=5
    )

    cost_score: Optional[int] = Field(
        default=None,
        ge=1,
        le=5
    )

    comments: Optional[str] = None


class ExpertEvaluationResponse(BaseModel):
    id: int
    decision_id: int
    alternative_id: int
    expert_id: int

    feasibility_score: int
    risk_score: int
    cost_score: int

    comments: Optional[str]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True