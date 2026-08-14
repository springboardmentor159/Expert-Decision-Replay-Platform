from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.decision import Decision
from app.schemas.decision import DecisionCreate, DecisionResponse


router = APIRouter(
    prefix="/decisions",
    tags=["Decision Management"]
)


# --------------------------------------------------
# CREATE DECISION
# --------------------------------------------------

@router.post(
    "",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_decision(
    decision_data: DecisionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    decision = Decision(
        title=decision_data.title,
        problem_statement=decision_data.problem_statement,
        category=decision_data.category,
        status="Draft",
        created_by=int(current_user)
    )

    db.add(decision)
    db.commit()
    db.refresh(decision)

    return decision


# --------------------------------------------------
# GET ALL DECISIONS
# --------------------------------------------------

@router.get(
    "",
    response_model=list[DecisionResponse]
)
def get_decisions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    decisions = db.query(Decision).all()

    return decisions


# --------------------------------------------------
# GET DECISION BY ID
# --------------------------------------------------

@router.get(
    "/{decision_id}",
    response_model=DecisionResponse
)
def get_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return decision