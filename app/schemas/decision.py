from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.decision_status import DecisionStatus


# ==========================================
# CREATE DECISION
# ==========================================
class DecisionCreate(BaseModel):
    title: str
    problem_statement: str
    category: str
    rationale: Optional[str] = None


# ==========================================
# UPDATE DECISION
# ==========================================
class DecisionUpdate(BaseModel):
    title: Optional[str] = None
    problem_statement: Optional[str] = None
    category: Optional[str] = None
    rationale: Optional[str] = None


# ==========================================
# UPDATE DECISION STATUS
# ==========================================
class DecisionStatusUpdate(BaseModel):
    status: DecisionStatus


# ==========================================
# DECISION RESPONSE
# ==========================================
class DecisionResponse(BaseModel):
    id: int
    title: str
    problem_statement: str
    category: str
    rationale: Optional[str] = None
    status: DecisionStatus
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==========================================
# PAGINATED DECISION RESPONSE
# ==========================================
class DecisionListResponse(BaseModel):
    items: List[DecisionResponse]
    page: int
    page_size: int
    total: int