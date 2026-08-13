from pydantic import BaseModel
from datetime import datetime


class DecisionCreate(BaseModel):
    title: str
    problem_statement: str
    category: str

class DecisionUpdate(BaseModel):
    title: str | None = None
    problem_statement: str | None = None
    category: str | None = None
    status: str | None = None



class DecisionResponse(BaseModel):
    id: int
    title: str
    problem_statement: str
    category: str
    status: str
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True