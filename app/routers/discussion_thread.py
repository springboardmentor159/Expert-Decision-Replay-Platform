from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.decision import Decision
from app.models.discussion_thread import DiscussionThread
from app.schemas.discussion_thread import (
    DiscussionThreadCreate,
    DiscussionThreadResponse,
    DiscussionThreadUpdate,
)


router = APIRouter(
    tags=["Discussion Threads"],
    dependencies=[Depends(get_current_user)]
)


# =========================================================
# CREATE DISCUSSION THREAD
# =========================================================

@router.post(
    "/decisions/{decision_id}/threads",
    response_model=DiscussionThreadResponse,
    status_code=201
)
def create_thread(
    decision_id: int,
    thread_data: DiscussionThreadCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Check whether Decision exists
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    # Get authenticated user's ID from JWT
    user_id = int(current_user["sub"])

    new_thread = DiscussionThread(
        decision_id=decision_id,
        created_by=user_id,
        title=thread_data.title,
        description=thread_data.description,
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
    response_model=List[DiscussionThreadResponse]
)
def get_threads(
    decision_id: int,
    db: Session = Depends(get_db)
):
    # Check whether Decision exists
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    threads = (
        db.query(DiscussionThread)
        .filter(
            DiscussionThread.decision_id == decision_id
        )
        .all()
    )

    return threads


# =========================================================
# GET DISCUSSION THREAD BY ID
# =========================================================

@router.get(
    "/threads/{thread_id}",
    response_model=DiscussionThreadResponse
)
def get_thread(
    thread_id: int,
    db: Session = Depends(get_db)
):
    thread = (
        db.query(DiscussionThread)
        .filter(DiscussionThread.id == thread_id)
        .first()
    )

    if not thread:
        raise HTTPException(
            status_code=404,
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
def update_thread(
    thread_id: int,
    thread_data: DiscussionThreadUpdate,
    db: Session = Depends(get_db)
):
    thread = (
        db.query(DiscussionThread)
        .filter(DiscussionThread.id == thread_id)
        .first()
    )

    if not thread:
        raise HTTPException(
            status_code=404,
            detail="Discussion thread not found"
        )

    thread.title = thread_data.title
    thread.description = thread_data.description
    thread.status = thread_data.status

    db.commit()
    db.refresh(thread)

    return thread


# =========================================================
# DELETE DISCUSSION THREAD
# =========================================================

@router.delete(
    "/threads/{thread_id}"
)
def delete_thread(
    thread_id: int,
    db: Session = Depends(get_db)
):
    thread = (
        db.query(DiscussionThread)
        .filter(DiscussionThread.id == thread_id)
        .first()
    )

    if not thread:
        raise HTTPException(
            status_code=404,
            detail="Discussion thread not found"
        )

    db.delete(thread)
    db.commit()

    return {
        "message": "Discussion thread deleted successfully"
    }