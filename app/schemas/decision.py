from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import DecisionStatus
from app.schemas.audit_log import AuditLogResponse
from app.schemas.decision_version import DecisionVersionResponse


class DecisionCreate(BaseModel):
    title: str
    problem_statement: str
    category: str


class DecisionUpdate(BaseModel):
    title: Optional[str] = None
    problem_statement: Optional[str] = None
    category: Optional[str] = None


class DecisionStatusUpdate(BaseModel):
    status: DecisionStatus


class DecisionRationaleUpdate(BaseModel):
    rationale: str


class DecisionResponse(BaseModel):
    id: int
    title: str
    problem_statement: str
    category: str
    status: str
    created_by: int
    rationale: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DecisionVersionListResponse(BaseModel):
    versions: List["DecisionVersionResponse"]


class DecisionHistoryResponse(BaseModel):
    items: List["AuditLogResponse"]

    model_config = ConfigDict(from_attributes=True)

