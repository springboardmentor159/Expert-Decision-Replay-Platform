from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict
from app.schemas.tag import TagResponse


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


class DecisionRationaleUpdate(BaseModel):
    rationale: str


class DecisionRationaleResponse(BaseModel):
    decision_id: int
    rationale: Optional[str] = None


class DecisionResponse(BaseModel):
    id: int
    title: str
    problem_statement: str
    category: str
    status: str
    rationale: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: datetime
    tags: Optional[List[TagResponse]] = []

    model_config = ConfigDict(from_attributes=True)


class DecisionSearchItem(BaseModel):
    id: int
    title: str
    category: str
    status: str
    tags: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DecisionSearchResponse(BaseModel):
    items: List[DecisionResponse] = []
    results: List[DecisionSearchItem] = []
    total: int
    page: int
    page_size: int


class TimelineEvent(BaseModel):
    event_type: str
    timestamp: datetime
    actor_id: Optional[int] = None
    actor_name: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class DecisionTimelineResponse(BaseModel):
    decision_id: int
    title: str
    current_status: str
    events: List[TimelineEvent]
