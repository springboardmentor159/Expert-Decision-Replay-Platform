from pydantic import BaseModel, Field


class DecisionRationaleUpdate(BaseModel):
    rationale: str = Field(min_length=1)