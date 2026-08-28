from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.models.discussion_thread import DiscussionThread
from app.schemas.discussion_thread import (
    DiscussionThreadCreate,
    DiscussionThreadUpdate,
    DiscussionThreadResponse,
)
from app.routers.users import get_current_user


router = APIRouter(
    tags=["Discussion Threads"]
)


# CREATE THREAD
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    new_thread = DiscussionThread(
        decision_id=decision_id,
        created_by=int(current_user["sub"]),
        title=thread_data.title,
        description=thread_data.description
    )

    db.add(new_thread)
    db.commit()
    db.refresh(new_thread)

    return new_thread


# GET ALL THREADS FOR A DECISION
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return (
        db.query(DiscussionThread)
        .filter(DiscussionThread.decision_id == decision_id)
        .all()
    )


# GET THREAD BY ID
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found"
        )

    return thread


# UPDATE THREAD
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found"
        )

    current_user_id = int(current_user["sub"])

    if thread.created_by != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own discussion thread"
        )

    thread.title = thread_data.title
    thread.description = thread_data.description
    thread.status = thread_data.status

    db.commit()
    db.refresh(thread)

    return thread


# DELETE THREAD
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found"
        )

    current_user_id = int(current_user["sub"])

    if thread.created_by != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own discussion thread"
        )

    db.delete(thread)
    db.commit()

    return None