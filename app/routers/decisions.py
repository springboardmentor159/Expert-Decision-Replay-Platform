from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.orm import Session
from app.models.alternative import Alternative
from app.models.comment import Comment
from app.models.discussion_thread import DiscussionThread

from app.schemas.decision_replay import DecisionReplayResponse
from app.db.database import get_db
from app.models.decision import Decision
from app.models.user import User
from app.schemas.decision_replay import (
    DecisionReplayResponse,
    DecisionHistoryResponse
)
from app.schemas.decision import (
    DecisionCreate,
    DecisionUpdate,
    DecisionStatusUpdate,
    DecisionRationaleUpdate,
    DecisionResponse
)
from app.core.security import get_current_user


router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)


# CREATE DECISION
@router.post(
    "",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_decision(
    decision_data: DecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_decision = Decision(
        title=decision_data.title,
        problem_statement=decision_data.problem_statement,
        category=decision_data.category,
        status="Draft",
        created_by=current_user.id
    )

    db.add(new_decision)
    db.commit()
    db.refresh(new_decision)

    return new_decision


# GET ALL DECISIONS + FILTERING
@router.get(
    "",
    response_model=List[DecisionResponse]
)
def get_decisions(
    status_filter: Optional[str] = Query(
        default=None,
        alias="status"
    ),
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Decision)

    # Filter by status
    if status_filter:
        query = query.filter(
            Decision.status == status_filter
        )

    # Filter by category
    if category:
        query = query.filter(
            Decision.category == category
        )

    return query.all()


# GET DECISION BY ID
@router.get(
    "/{decision_id}",
    response_model=DecisionResponse
)
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return decision


# UPDATE DECISION
@router.put(
    "/{decision_id}",
    response_model=DecisionResponse
)
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    # Only allowed fields are updated
    decision.title = decision_data.title
    decision.problem_statement = decision_data.problem_statement
    decision.category = decision_data.category

    db.commit()
    db.refresh(decision)

    return decision


# UPDATE DECISION STATUS
@router.patch(
    "/{decision_id}/status",
    response_model=DecisionResponse
)
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    # Status is controlled by DecisionStatus enum
    decision.status = status_data.status

    db.commit()
    db.refresh(decision)

    return decision
# DECISION REPLAY
@router.get(
    "/{decision_id}/replay",
    response_model=DecisionReplayResponse
)
def replay_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get decision
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    # Get alternatives
    alternatives = db.query(Alternative).filter(
        Alternative.decision_id == decision_id
    ).all()

    # Get decision comments
    decision_comments = db.query(Comment).filter(
        Comment.decision_id == decision_id,
        Comment.thread_id.is_(None)
    ).all()

    # Get discussion threads
    threads = db.query(DiscussionThread).filter(
        DiscussionThread.decision_id == decision_id
    ).all()

    replay_threads = []

    for thread in threads:
        # Get replies/comments for this thread
        thread_comments = db.query(Comment).filter(
            Comment.thread_id == thread.id
        ).all()

        replay_threads.append({
            "id": thread.id,
            "title": thread.title,
            "description": thread.description,
            "comments": thread_comments
        })

    return {
        "decision_id": decision.id,
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category,
        "status": decision.status,
        "created_by": decision.created_by,
        "created_at": decision.created_at,

        "alternatives": alternatives,

        "comments": decision_comments,

        "discussion_threads": replay_threads
    }
# DECISION HISTORY
@router.get(
    "/{decision_id}/history",
    response_model=DecisionHistoryResponse
)
def get_decision_history(
    decision_id: int,
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

    return decision
# UPDATE DECISION RATIONALE
@router.put(
    "/{decision_id}/rationale",
    response_model=DecisionResponse
)
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    decision.rationale = rationale_data.rationale

    db.commit()
    db.refresh(decision)

    return decision