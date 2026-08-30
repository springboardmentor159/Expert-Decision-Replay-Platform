from pydantic import BaseModel


class AlternativeScore(BaseModel):
    alternative_id: int
    alternative_name: str
    feasibility_score: float
    risk_score: float
    cost_score: float
    total_score: float


class DecisionScoringResponse(BaseModel):
    decision_id: int
    alternatives: list[AlternativeScore]
    recommended_alternative_id: int | None