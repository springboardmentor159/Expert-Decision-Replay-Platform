from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


# CREATE DECISION
class DecisionCreate(BaseModel):
    title: str
    problem_statement: str
    category: "DecisionCategory"
    rationale: str | None = None


# UPDATE DECISION
class DecisionUpdate(BaseModel):
    title: str
    problem_statement: str
    category: "DecisionCategory"
    rationale: str | None = None


# DECISION STATUS
class DecisionStatus(str, Enum):
    Draft = "Draft"
    Approved = "Approved"
    Rejected = "Rejected"
    Under_Review = "Under Review"
    Archived = "Archived"


class DecisionCategory(str, Enum):
    Technology = "Technology"
    Finance = "Finance"
    Operations = "Operations"
    Human_Resources = "Human Resources"
    Security = "Security"
    Product = "Product"
    Infrastructure = "Infrastructure"
    Strategy = "Strategy"

# UPDATE STATUS
class DecisionStatusUpdate(BaseModel):
    status: DecisionStatus


# RESPONSE
class DecisionResponse(BaseModel):
    id: int
    title: str
    problem_statement: str
    category: str
    status: str
    rationale: str | None = None
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TagSummary(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class DecisionDiscoveryResponse(BaseModel):
    id: int
    title: str
    category: str
    status: str
    tags: list[TagSummary] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedDecisionResponse(BaseModel):
    items: list[DecisionDiscoveryResponse]
    page: int
    page_size: int
    total: int


class TimelineEvent(BaseModel):
    event_type: str
    description: str
    occurred_at: datetime
