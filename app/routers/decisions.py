from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.decision import (
    DecisionCreate,
    DecisionUpdate,
    DecisionResponse,
    DecisionStatus,
    DecisionStatusUpdate,
    DecisionRationaleUpdate
)
router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)


@router.post("/", response_model=DecisionResponse)
def create_decision(
    decision: DecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_decision = Decision(
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status="Draft",
        created_by=current_user.id
    )

    db.add(new_decision)
    db.commit()
    db.refresh(new_decision)

    return new_decision


@router.get("/", response_model=list[DecisionResponse])
def get_all_decisions(
    status: DecisionStatus | None = Query(default=None),
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Decision)

    if status is not None:
        query = query.filter(Decision.status == status.value)

    if category is not None:
        query = query.filter(Decision.category == category)

    return query.all()


@router.get("/{decision_id}", response_model=DecisionResponse)
def get_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    return decision


@router.put("/{decision_id}", response_model=DecisionResponse)
def update_decision(
    decision_id: int,
    decision_data: DecisionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    if decision_data.title is not None:
        decision.title = decision_data.title

    if decision_data.problem_statement is not None:
        decision.problem_statement = decision_data.problem_statement

    if decision_data.category is not None:
        decision.category = decision_data.category

    db.commit()
    db.refresh(decision)

    return decision


@router.patch("/{decision_id}/status", response_model=DecisionResponse)
def update_decision_status(
    decision_id: int,
    status_data: DecisionStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    decision.status = status_data.status.value

    db.commit()
    db.refresh(decision)

    return decision


@router.delete("/{decision_id}")
def delete_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    db.delete(decision)
    db.commit()

    return {
        "message": "Decision deleted successfully"
    }
@router.put("/{decision_id}/rationale")
def update_decision_rationale(
    decision_id: int,
    rationale_data: DecisionRationaleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    if decision.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to update this decision rationale"
        )

    decision.rationale = rationale_data.rationale

    db.commit()
    db.refresh(decision)

    return {
        "message": "Decision rationale updated successfully",
        "decision_id": decision.id,
        "rationale": decision.rationale
    }


@router.get("/{decision_id}/rationale")
def get_decision_rationale(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    return {
        "decision_id": decision.id,
        "rationale": decision.rationale
    }