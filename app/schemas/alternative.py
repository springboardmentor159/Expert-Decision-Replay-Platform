from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, field_validator


class RiskLevel(str, Enum):
    """Enum for Risk Level values"""
    Low = "Low"
    Medium = "Medium"
    High = "High"
    Critical = "Critical"


class AlternativeBase(BaseModel):
    """Base schema for Alternative data"""
    name: str
    description: str
    pros: str
    cons: str
    estimated_cost: int
    feasibility_score: int
    risk_level: str

    @field_validator("feasibility_score")
    @classmethod
    def validate_feasibility_score(cls, v: int) -> int:
        """Validate feasibility score is between 1 and 5"""
        if not isinstance(v, int) or v < 1 or v > 5:
            raise ValueError("feasibility_score must be an integer between 1 and 5")
        return v

    @field_validator("risk_level")
    @classmethod
    def validate_risk_level(cls, v: str) -> str:
        """Validate risk level is one of the allowed values"""
        allowed_values = {"Low", "Medium", "High", "Critical"}
        if v not in allowed_values:
            raise ValueError(f"risk_level must be one of {allowed_values}")
        return v


class AlternativeCreate(AlternativeBase):
    """Schema for creating a new alternative"""
    pass


class AlternativeUpdate(BaseModel):
    """Schema for updating an alternative"""
    name: str | None = None
    description: str | None = None
    pros: str | None = None
    cons: str | None = None
    estimated_cost: int | None = None
    feasibility_score: int | None = None
    risk_level: str | None = None

    @field_validator("feasibility_score")
    @classmethod
    def validate_feasibility_score(cls, v: int | None) -> int | None:
        """Validate feasibility score is between 1 and 5"""
        if v is not None and (not isinstance(v, int) or v < 1 or v > 5):
            raise ValueError("feasibility_score must be an integer between 1 and 5")
        return v

    @field_validator("risk_level")
    @classmethod
    def validate_risk_level(cls, v: str | None) -> str | None:
        """Validate risk level is one of the allowed values"""
        if v is not None:
            allowed_values = {"Low", "Medium", "High", "Critical"}
            if v not in allowed_values:
                raise ValueError(f"risk_level must be one of {allowed_values}")
        return v


class AlternativeResponse(AlternativeBase):
    """Schema for alternative response"""
    id: int
    decision_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlternativeComparisonItem(BaseModel):
    """Schema for alternative comparison item"""
    name: str
    estimated_cost: int
    feasibility_score: int
    risk_level: str

    model_config = ConfigDict(from_attributes=True)


class AlternativeComparison(BaseModel):
    """Schema for alternative comparison response"""
    decision_id: int
    alternatives: list[AlternativeComparisonItem]

    model_config = ConfigDict(from_attributes=True)
