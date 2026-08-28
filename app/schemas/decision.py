from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, field_validator


class DecisionCategory(str, Enum):
    TECHNOLOGY = "Technology"
    FINANCE = "Finance"
    OPERATIONS = "Operations"
    HUMAN_RESOURCES = "Human Resources"
    SECURITY = "Security"
    PRODUCT = "Product"
    INFRASTRUCTURE = "Infrastructure"
    STRATEGY = "Strategy"


class DecisionStatus(str, Enum):
    DRAFT = "Draft"
    UNDER_REVIEW = "Under Review"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    ARCHIVED = "Archived"


class DecisionCreate(BaseModel):
    title: str
    problem_statement: str
    category: str


class DecisionUpdate(BaseModel):
    title: str
    problem_statement: str
    category: str


class DecisionStatusUpdate(BaseModel):
    status: DecisionStatus


class DecisionResponse(BaseModel):
    id: int
    title: str
    problem_statement: str
    category: str
    status: str
    rationale: Optional[str] = None
    created_by: int
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime

    @field_validator("tags", mode="before")
    @classmethod
    def serialize_tags(cls, v: Any) -> List[str]:
        if not v:
            return []
        if isinstance(v, list):
            result = []
            for item in v:
                if isinstance(item, str):
                    result.append(item)
                elif hasattr(item, "name"):
                    result.append(item.name)
                elif isinstance(item, dict) and "name" in item:
                    result.append(item["name"])
            return result
        return []

    model_config = ConfigDict(from_attributes=True)


class DecisionRationaleUpdate(BaseModel):
    rationale: str


class DecisionRationaleResponse(BaseModel):
    decision_id: int
    rationale: Optional[str] = None


class PaginatedDecisionsResponse(BaseModel):
    items: List[DecisionResponse]
    page: int
    page_size: int
    total: int
    results: Optional[List[DecisionResponse]] = None


class DecisionTimelineEvent(BaseModel):
    id: Optional[int] = None
    event_type: str
    description: str
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    timestamp: datetime


class DecisionTimelineResponse(BaseModel):
    decision_id: int
    decision_title: str
    current_status: str
    events: List[DecisionTimelineEvent]
