from datetime import datetime
from pydantic import BaseModel


class DecisionRationaleUpdate(BaseModel):
    rationale: str


class DecisionRationaleResponse(BaseModel):
    decision_id: int
    rationale: str | None
    updated_at: datetime