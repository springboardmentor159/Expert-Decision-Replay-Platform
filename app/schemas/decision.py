from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict

from app.schemas.tag import TagResponse


class DecisionStatus(str, Enum):
    """Enum for Decision status values"""
    Draft = "Draft"
    UnderReview = "Under Review"
    Approved = "Approved"
    Rejected = "Rejected"
    Archived = "Archived"


class DecisionCategory(str, Enum):
    Technology = "Technology"
    Finance = "Finance"
    Operations = "Operations"
    HumanResources = "Human Resources"
    Security = "Security"
    Product = "Product"
    Infrastructure = "Infrastructure"
    Strategy = "Strategy"


class DecisionBase(BaseModel):
    """Base schema for Decision data"""
    title: str
    problem_statement: str
    category: DecisionCategory


class DecisionCreate(DecisionBase):
    """Schema for creating a new decision"""
    pass


class DecisionUpdate(BaseModel):
    """Schema for updating a decision"""
    title: str | None = None
    problem_statement: str | None = None
    category: DecisionCategory | None = None


class DecisionStatusUpdate(BaseModel):
    """Schema for updating decision status"""
    status: DecisionStatus


class DecisionRationaleUpdate(BaseModel):
    """Schema for updating decision rationale"""
    rationale: str


class DecisionResponse(DecisionBase):
    """Schema for decision response"""
    category: str
    id: int
    status: str
    rationale: str | None = None
    created_by: int
    created_at: datetime
    updated_at: datetime
    tags: list[TagResponse] = []

    model_config = ConfigDict(from_attributes=True)


class DecisionFilterResponse(BaseModel):
    """Schema for filtered decision responses"""
    decisions: list[DecisionResponse]
    total: int


class DecisionDiscoveryResponse(BaseModel):
    items: list[DecisionResponse]
    page: int
    page_size: int
    total: int


class DecisionSearchResponse(DecisionDiscoveryResponse):
    results: list[DecisionResponse]
