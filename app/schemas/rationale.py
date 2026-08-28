from pydantic import BaseModel


class RationaleUpdate(BaseModel):
    rationale: str


class RationaleResponse(BaseModel):
    decision_id: int
    rationale: str | None