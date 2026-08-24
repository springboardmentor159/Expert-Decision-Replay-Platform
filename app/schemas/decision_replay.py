from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List


class ReplayAlternative(BaseModel):
    id: int
    name: str
    estimated_cost: float
    feasibility_score: int
    risk_level: str

    model_config = ConfigDict(from_attributes=True)


class ReplayComment(BaseModel):
    id: int
    user_id: int
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReplayThread(BaseModel):
    id: int
    title: str
    description: str
    comments: List[ReplayComment] = []

    model_config = ConfigDict(from_attributes=True)


class DecisionReplayResponse(BaseModel):
    decision_id: int
    title: str
    problem_statement: str
    category: str
    status: str
    created_by: int
    created_at: datetime

    alternatives: List[ReplayAlternative] = []
    comments: List[ReplayComment] = []
    discussion_threads: List[ReplayThread] = []

    model_config = ConfigDict(from_attributes=True)
class DecisionHistoryResponse(BaseModel):
    id: int
    title: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)