from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.models.discussion_thread import DiscussionThread
from app.models.user import User
from app.schemas.discussion_thread import (
    DiscussionThreadCreate,
    DiscussionThreadUpdate,
    DiscussionThreadResponse
)
from app.routers.auth import get_current_user


router = APIRouter(
    tags=["Discussion Threads"]
)


# =========================================================
# CREATE DISCUSSION THREAD
# =========================================================

@router.post(
    "/decisions/{decision_id}/threads",
    response_model=DiscussionThreadResponse,
    status_code=status.HTTP_201_CREATED
)
def create_discussion_thread(
    decision_id: int,
    thread: DiscussionThreadCreate,
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

    new_thread = DiscussionThread(
        decision_id=decision_id,
        created_by=current_user.id,
        title=thread.title,
        description=thread.description,
        status="Open"
    )

    db.add(new_thread)
    db.commit()
    db.refresh(new_thread)

    return new_thread


# =========================================================
# GET ALL DISCUSSION THREADS FOR A DECISION
# =========================================================

@router.get(
    "/decisions/{decision_id}/threads",
    response_model=list[DiscussionThreadResponse]
)
def get_discussion_threads(
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

    threads = db.query(DiscussionThread).filter(
        DiscussionThread.decision_id == decision_id
    ).all()

    return threads


# =========================================================
# GET ONE DISCUSSION THREAD
# =========================================================

@router.get(
    "/threads/{thread_id}",
    response_model=DiscussionThreadResponse
)
def get_discussion_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = db.query(DiscussionThread).filter(
        DiscussionThread.id == thread_id
    ).first()

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found"
        )

    return thread


# =========================================================
# UPDATE DISCUSSION THREAD
# =========================================================

@router.put(
    "/threads/{thread_id}",
    response_model=DiscussionThreadResponse
)
def update_discussion_thread(
    thread_id: int,
    thread_data: DiscussionThreadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = db.query(DiscussionThread).filter(
        DiscussionThread.id == thread_id
    ).first()

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found"
        )

         # Ownership check
    if thread.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update this discussion thread"
        )

    if thread_data.title is not None:
        thread.title = thread_data.title

    if thread_data.description is not None:
        thread.description = thread_data.description

    db.commit()
    db.refresh(thread)

    return thread


# =========================================================
# DELETE DISCUSSION THREAD
# =========================================================

@router.delete(
    "/threads/{thread_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_discussion_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = db.query(DiscussionThread).filter(
        DiscussionThread.id == thread_id
    ).first()

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found"
        )
    # Ownership check
    if thread.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to delete this discussion thread"
        )

    db.delete(thread)
    db.commit()

    return None
