from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.decision import Decision
from app.models.user import User
from app.schemas.decision import (
    DecisionCreate,
    DecisionResponse,
    DecisionUpdate,
    DecisionStatusUpdate,
    DecisionStatus,
    DecisionRationaleUpdate,
    DecisionRationaleResponse
)

router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)

@router.post(
    "",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED
)
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

@router.get(
    "",
    response_model=List[DecisionResponse]
)
def get_decisions(
    status: Optional[DecisionStatus] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Decision)
    if status:
        query = query.filter(Decision.status == status.value)
    if category:
        query = query.filter(Decision.category == category)
    return query.all()

@router.get(
    "/{decision_id}",
    response_model=DecisionResponse
)
def get_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )
    return decision

@router.put(
    "/{decision_id}",
    response_model=DecisionResponse
)
def update_decision(
    decision_id: int,
    decision_update: DecisionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )
    
    decision.title = decision_update.title
    decision.problem_statement = decision_update.problem_statement
    decision.category = decision_update.category
    
    db.commit()
    db.refresh(decision)
    return decision

@router.patch(
    "/{decision_id}/status",
    response_model=DecisionResponse
)
def update_decision_status(
    decision_id: int,
    status_update: DecisionStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )
    
    decision.status = status_update.status.value
    
    db.commit()
    db.refresh(decision)
    return decision


@router.put(
    "/{decision_id}/rationale",
    response_model=DecisionRationaleResponse,
    status_code=status.HTTP_200_OK,
    summary="Record decision rationale"
)
def update_decision_rationale(
    decision_id: int,
    rationale_update: DecisionRationaleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    if decision.created_by != current_user.id and current_user.role not in ["Administrator", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update decision rationale"
        )

    decision.rationale = rationale_update.rationale
    db.commit()
    db.refresh(decision)

    return DecisionRationaleResponse(
        decision_id=decision.id,
        rationale=decision.rationale
    )


@router.get(
    "/{decision_id}/rationale",
    response_model=DecisionRationaleResponse,
    status_code=status.HTTP_200_OK,
    summary="Get decision rationale"
)
def get_decision_rationale(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return DecisionRationaleResponse(
        decision_id=decision.id,
        rationale=decision.rationale
    )

