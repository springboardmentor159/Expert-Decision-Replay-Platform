from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.decision import Decision
from app.schemas.decision import (
    DecisionCreate,
    DecisionUpdate,
    DecisionStatusUpdate,
    DecisionResponse,
    DecisionRationaleUpdate,
    DecisionRationaleResponse,
)


router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"],
)


# =========================
# CREATE DECISION
# =========================

@router.post(
    "",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_decision(
    decision_data: DecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_decision = Decision(
        title=decision_data.title,
        problem_statement=decision_data.problem_statement,
        category=decision_data.category,
        status="Draft",
        created_by=current_user.id,
    )

    db.add(new_decision)
    db.commit()
    db.refresh(new_decision)

    return new_decision


# =========================
# GET ALL DECISIONS
# WITH FILTERING
# =========================

@router.get(
    "",
    response_model=List[DecisionResponse],
)
def get_decisions(
    status_filter: Optional[str] = Query(
        default=None,
        alias="status",
    ),
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Decision)

    if status_filter is not None:
        query = query.filter(Decision.status == status_filter)

    if category is not None:
        query = query.filter(Decision.category == category)

    return query.all()


# =========================
# UPDATE DECISION RATIONALE
# =========================

@router.put(
    "/{decision_id}/rationale",
    response_model=DecisionRationaleResponse,
)
def update_decision_rationale(
    decision_id: int,
    rationale_data: DecisionRationaleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    # Only the decision creator can update the rationale
    if decision.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this decision rationale",
        )

    decision.rationale = rationale_data.rationale

    db.commit()
    db.refresh(decision)

    return {
        "decision_id": decision.id,
        "rationale": decision.rationale,
    }


# =========================
# GET DECISION RATIONALE
# =========================

@router.get(
    "/{decision_id}/rationale",
    response_model=DecisionRationaleResponse,
)
def get_decision_rationale(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    return {
        "decision_id": decision.id,
        "rationale": decision.rationale,
    }


# =========================
# GET DECISION BY ID
# =========================

@router.get(
    "/{decision_id}",
    response_model=DecisionResponse,
)
def get_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    return decision


# =========================
# UPDATE DECISION
# =========================

@router.put(
    "/{decision_id}",
    response_model=DecisionResponse,
)
def update_decision(
    decision_id: int,
    decision_data: DecisionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    decision.title = decision_data.title
    decision.problem_statement = decision_data.problem_statement
    decision.category = decision_data.category

    db.commit()
    db.refresh(decision)

    return decision


# =========================
# UPDATE DECISION STATUS
# =========================

@router.patch(
    "/{decision_id}/status",
    response_model=DecisionResponse,
)
def update_decision_status(
    decision_id: int,
    status_data: DecisionStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    decision.status = status_data.status

    db.commit()
    db.refresh(decision)

    return decision