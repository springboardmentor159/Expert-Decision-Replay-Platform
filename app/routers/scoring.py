from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.models.alternative import Alternative
from app.schemas.scoring import (
    AlternativeScore,
    DecisionScoringResponse
)


router = APIRouter(
    prefix="/scoring",
    tags=["Decision Scoring"]
)


def calculate_risk_score(risk_level):
    risk_mapping = {
        "Low": 100,
        "Medium": 60,
        "High": 30
    }

    return risk_mapping.get(
        risk_level.value if hasattr(risk_level, "value") else str(risk_level),
        0
    )


@router.get(
    "/decision/{decision_id}",
    response_model=DecisionScoringResponse
)
def score_decision(
    decision_id: int,
    db: Session = Depends(get_db)
):

    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    alternatives = db.query(Alternative).filter(
        Alternative.decision_id == decision_id
    ).all()

    if not alternatives:
        raise HTTPException(
            status_code=404,
            detail="No alternatives found for this decision"
        )

    max_cost = max(
        alternative.estimated_cost
        for alternative in alternatives
    )

    results = []

    for alternative in alternatives:

        # Feasibility: convert 1-5 score into 0-100
        feasibility_score = (
            alternative.feasibility_score / 5
        ) * 100

        # Risk score
        risk_score = calculate_risk_score(
            alternative.risk_level
        )

        # Cost score
        # Lower cost = higher score
        if max_cost > 0:
            cost_score = (
                1 - alternative.estimated_cost / max_cost
            ) * 100
        else:
            cost_score = 100

        # Weighted total score
        total_score = (
            feasibility_score * 0.40
            + risk_score * 0.30
            + cost_score * 0.30
        )

        results.append(
            AlternativeScore(
                alternative_id=alternative.id,
                alternative_name=alternative.name,
                feasibility_score=round(
                    feasibility_score,
                    2
                ),
                risk_score=round(
                    risk_score,
                    2
                ),
                cost_score=round(
                    cost_score,
                    2
                ),
                total_score=round(
                    total_score,
                    2
                )
            )
        )

    # Sort highest score first
    results.sort(
        key=lambda item: item.total_score,
        reverse=True
    )

    recommended_alternative_id = results[0].alternative_id

    return DecisionScoringResponse(
        decision_id=decision_id,
        alternatives=results,
        recommended_alternative_id=recommended_alternative_id
    )