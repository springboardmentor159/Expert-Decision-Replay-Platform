from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ApprovalCreate(BaseModel):
    decision_id: int
    reviewer_id: int
    approval_level: int = Field(default=1, ge=1)
    

class ApprovalUpdate(BaseModel):
    status: str
    completed_at: Optional[datetime] = None


class ApprovalResponse(BaseModel):
    id: int
    decision_id: int
    reviewer_id: int
    approval_level: int
    status: str
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)