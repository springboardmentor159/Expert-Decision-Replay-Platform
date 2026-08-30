from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.models.alternative import Alternative
from app.models.expert_evaluation import ExpertEvaluation
from app.models.user import User

from app.schemas.expert_evaluation import (
    ExpertEvaluationCreate,
    ExpertEvaluationUpdate,
    ExpertEvaluationResponse
)

from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/expert-evaluations",
    tags=["Expert Evaluations"]
)


# -----------------------------------------
# CREATE EXPERT EVALUATION
# -----------------------------------------

@router.post(
    "/decision/{decision_id}",
    response_model=ExpertEvaluationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_expert_evaluation(
    decision_id: int,
    evaluation_data: ExpertEvaluationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    alternative = db.query(Alternative).filter(
        Alternative.id == evaluation_data.alternative_id,
        Alternative.decision_id == decision_id
    ).first()

    if not alternative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alternative not found for this decision"
        )

    existing_evaluation = db.query(ExpertEvaluation).filter(
        ExpertEvaluation.decision_id == decision_id,
        ExpertEvaluation.alternative_id == evaluation_data.alternative_id,
        ExpertEvaluation.expert_id == current_user.id
    ).first()

    if existing_evaluation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already evaluated this alternative"
        )

    new_evaluation = ExpertEvaluation(
        decision_id=decision_id,
        alternative_id=evaluation_data.alternative_id,
        expert_id=current_user.id,
        feasibility_score=evaluation_data.feasibility_score,
        risk_score=evaluation_data.risk_score,
        cost_score=evaluation_data.cost_score,
        comments=evaluation_data.comments
    )

    db.add(new_evaluation)
    db.commit()
    db.refresh(new_evaluation)

    return new_evaluation


# -----------------------------------------
# GET ALL EVALUATIONS FOR A DECISION
# -----------------------------------------

@router.get(
    "/decision/{decision_id}",
    response_model=list[ExpertEvaluationResponse]
)
def get_decision_evaluations(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    evaluations = db.query(ExpertEvaluation).filter(
        ExpertEvaluation.decision_id == decision_id
    ).all()

    return evaluations


# -----------------------------------------
# GET ONE EVALUATION
# -----------------------------------------

@router.get(
    "/{evaluation_id}",
    response_model=ExpertEvaluationResponse
)
def get_expert_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    evaluation = db.query(ExpertEvaluation).filter(
        ExpertEvaluation.id == evaluation_id
    ).first()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert evaluation not found"
        )

    return evaluation


# -----------------------------------------
# UPDATE OWN EVALUATION
# -----------------------------------------

@router.put(
    "/{evaluation_id}",
    response_model=ExpertEvaluationResponse
)
def update_expert_evaluation(
    evaluation_id: int,
    evaluation_data: ExpertEvaluationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    evaluation = db.query(ExpertEvaluation).filter(
        ExpertEvaluation.id == evaluation_id
    ).first()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert evaluation not found"
        )

    if evaluation.expert_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own evaluation"
        )

    update_data = evaluation_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(evaluation, key, value)

    db.commit()
    db.refresh(evaluation)

    return evaluation


# -----------------------------------------
# DELETE OWN EVALUATION
# -----------------------------------------

@router.delete(
    "/{evaluation_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_expert_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    evaluation = db.query(ExpertEvaluation).filter(
        ExpertEvaluation.id == evaluation_id
    ).first()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert evaluation not found"
        )

    if evaluation.expert_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own evaluation"
        )

    db.delete(evaluation)
    db.commit()

    return None