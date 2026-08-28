from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.discussion_thread import DiscussionThread
from app.models.decision import Decision
from app.models.activity import Activity
from app.schemas.discussion_thread import (
    DiscussionThreadCreate,
    DiscussionThreadUpdate,
    DiscussionThreadResponse
)
from app.core.security import get_current_user


router = APIRouter(
    tags=["Discussion Threads"]
)


# ============================================================
# CREATE DISCUSSION THREAD
# POST /decisions/{decision_id}/threads
# ============================================================

@router.post(
    "/decisions/{decision_id}/threads",
    response_model=DiscussionThreadResponse,
    status_code=status.HTTP_201_CREATED
)
def create_thread(
    decision_id: int,
    thread_data: DiscussionThreadCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
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

    new_thread = DiscussionThread(
        decision_id=decision_id,
        created_by=current_user.id,
        title=thread_data.title,
        description=thread_data.description,
        status="Open"
    )

    db.add(new_thread)
    db.commit()
    db.refresh(new_thread)

    # Activity log
    activity = Activity(
        user_id=current_user.id,
        action="Discussion Thread Created",
        entity_type="DiscussionThread",
        entity_id=new_thread.id,
        description=(
            f"User {current_user.id} created "
            f"Discussion Thread {new_thread.id} "
            f"for Decision {decision_id}"
        )
    )

    db.add(activity)
    db.commit()

    return new_thread


# ============================================================
# GET ALL THREADS FOR A DECISION
# GET /decisions/{decision_id}/threads
# ============================================================

@router.get(
    "/decisions/{decision_id}/threads",
    response_model=List[DiscussionThreadResponse]
)
def get_threads(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
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

    return (
        db.query(DiscussionThread)
        .filter(DiscussionThread.decision_id == decision_id)
        .all()
    )


# ============================================================
# GET THREAD BY ID
# GET /threads/{thread_id}
# ============================================================

@router.get(
    "/threads/{thread_id}",
    response_model=DiscussionThreadResponse
)
def get_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
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


# ============================================================
# UPDATE THREAD
# PUT /threads/{thread_id}
# ============================================================

@router.put(
    "/threads/{thread_id}",
    response_model=DiscussionThreadResponse
)
def update_thread(
    thread_id: int,
    thread_data: DiscussionThreadUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
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

    # Only the thread owner can update it
    if thread.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own discussion threads"
        )

    thread.title = thread_data.title
    thread.description = thread_data.description
    thread.status = thread_data.status

    db.commit()
    db.refresh(thread)

    # Activity log
    activity = Activity(
        user_id=current_user.id,
        action="Discussion Thread Updated",
        entity_type="DiscussionThread",
        entity_id=thread.id,
        description=(
            f"User {current_user.id} updated "
            f"Discussion Thread {thread.id}"
        )
    )

    db.add(activity)
    db.commit()

    return thread


# ============================================================
# DELETE THREAD
# DELETE /threads/{thread_id}
# ============================================================

@router.delete(
    "/threads/{thread_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
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

    # Only the thread owner can delete it
    if thread.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own discussion threads"
        )

    db.delete(thread)
    db.commit()

    return None