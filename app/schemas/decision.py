from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


# ============================================================
# DECISION STATUS
# ============================================================

DecisionStatus = Literal[
    "Draft",
    "Under Review",
    "Approved",
    "Rejected",
    "Archived",
]


# ============================================================
# CREATE DECISION
# ============================================================

class DecisionCreate(BaseModel):
    title: str
    problem_statement: str
    category: str


# ============================================================
# UPDATE DECISION
# ============================================================

class DecisionUpdate(BaseModel):
    title: str
    problem_statement: str
    category: str


# ============================================================
# UPDATE DECISION STATUS
# ============================================================

class DecisionStatusUpdate(BaseModel):
    status: DecisionStatus


# ============================================================
# DECISION RESPONSE
# ============================================================

class DecisionResponse(BaseModel):
    id: int
    title: str
    problem_statement: str
    category: str
    status: DecisionStatus

    # User who created the decision
    created_by: int

    # Decision rationale
    rationale: str | None = None

    # Timestamps
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# UPDATE DECISION RATIONALE
# ============================================================

class DecisionRationaleUpdate(BaseModel):
    rationale: str


# ============================================================
# DECISION RATIONALE RESPONSE
# ============================================================

class DecisionRationaleResponse(BaseModel):
    decision_id: int
    rationale: str | None

    model_config = ConfigDict(from_attributes=True)
    # ============================================================
# DECISION TIMELINE
# ============================================================

class DecisionTimelineEvent(BaseModel):
    event_type: str
    description: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)