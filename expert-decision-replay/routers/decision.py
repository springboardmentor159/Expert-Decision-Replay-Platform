from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.schemas.decision import (
    DecisionCreate,
    DecisionUpdate,
    DecisionStatusUpdate,
    DecisionResponse,
)
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/decisions",
    tags=["Decision Management"]
)


# ==================================================
# CREATE DECISION
# POST /decisions
# ==================================================

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


# ==================================================
# GET ALL DECISIONS + FILTERING
# GET /decisions
# GET /decisions?status=Draft
# GET /decisions?category=Technology
# GET /decisions?status=Approved&category=Technology
# ==================================================

@router.get(
    "",
    response_model=list[DecisionResponse]
)
def get_decisions(
    status: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    query = db.query(Decision)

    # Filter by status
    if status:
        query = query.filter(
            Decision.status == status
        )

    # Filter by category
    if category:
        query = query.filter(
            Decision.category == category
        )

    decisions = query.all()

    return decisions


# ==================================================
# GET DECISION BY ID
# GET /decisions/{decision_id}
# ==================================================

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


# ==================================================
# UPDATE DECISION
# PUT /decisions/{decision_id}
# ==================================================

@router.put(
    "/{decision_id}",
    response_model=DecisionResponse
)
def update_decision(
    decision_id: int,
    decision_data: DecisionUpdate,
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

    # Only these fields can be changed
    decision.title = decision_data.title
    decision.problem_statement = decision_data.problem_statement
    decision.category = decision_data.category

    # Do NOT change:
    # decision.id
    # decision.created_by
    # decision.created_at

    db.commit()
    db.refresh(decision)

    return decision


# ==================================================
# UPDATE DECISION STATUS
# PATCH /decisions/{decision_id}/status
# ==================================================

@router.patch(
    "/{decision_id}/status",
    response_model=DecisionResponse
)
def update_decision_status(
    decision_id: int,
    status_data: DecisionStatusUpdate,
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

    # Status is already validated by DecisionStatusUpdate
    decision.status = status_data.status.value

    db.commit()
    db.refresh(decision)

    return decision