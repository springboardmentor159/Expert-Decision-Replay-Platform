from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.thread import DiscussionThread
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.thread import (
    ThreadCreate,
    ThreadResponse,
    ThreadUpdate
)
from app.services.auth import get_current_user


router = APIRouter(
    tags=["Discussion Threads"]
)


# Create a discussion thread for a decision
@router.post(
    "/decisions/{decision_id}/threads",
    response_model=ThreadResponse,
    status_code=status.HTTP_201_CREATED
)
def create_thread(
    decision_id: int,
    thread_data: ThreadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    thread = DiscussionThread(
        decision_id=decision.id,
        title=thread_data.title,
        created_by=current_user.id
    )

    db.add(thread)
    db.commit()
    db.refresh(thread)

    return thread


# Get all discussion threads for a decision
@router.get(
    "/decisions/{decision_id}/threads",
    response_model=list[ThreadResponse]
)
def get_decision_threads(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    threads = (
        db.query(DiscussionThread)
        .filter(DiscussionThread.decision_id == decision_id)
        .order_by(DiscussionThread.created_at)
        .all()
    )

    return threads


# Get a discussion thread by ID
@router.get(
    "/threads/{thread_id}",
    response_model=ThreadResponse
)
def get_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = (
        db.query(DiscussionThread)
        .filter(DiscussionThread.id == thread_id)
        .first()
    )

    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found"
        )

    return thread


# Update a discussion thread
@router.put(
    "/threads/{thread_id}",
    response_model=ThreadResponse
)
def update_thread(
    thread_id: int,
    thread_data: ThreadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = (
        db.query(DiscussionThread)
        .filter(DiscussionThread.id == thread_id)
        .first()
    )

    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found"
        )

    if thread.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own discussion threads"
        )

    thread.title = thread_data.title

    db.commit()
    db.refresh(thread)

    return thread


# Delete a discussion thread
@router.delete(
    "/threads/{thread_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = (
        db.query(DiscussionThread)
        .filter(DiscussionThread.id == thread_id)
        .first()
    )

    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found"
        )

    if thread.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own discussion threads"
        )

    db.delete(thread)
    db.commit()

    return None


# Add a reply to a discussion thread
@router.post(
    "/threads/{thread_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_thread_reply(
    thread_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = (
        db.query(DiscussionThread)
        .filter(DiscussionThread.id == thread_id)
        .first()
    )

    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found"
        )

    comment = Comment(
        decision_id=thread.decision_id,
        user_id=current_user.id,
        thread_id=thread.id,
        content=comment_data.content
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


# Get all replies for a discussion thread
@router.get(
    "/threads/{thread_id}/comments",
    response_model=list[CommentResponse]
)
def get_thread_replies(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = (
        db.query(DiscussionThread)
        .filter(DiscussionThread.id == thread_id)
        .first()
    )

    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found"
        )

    comments = (
        db.query(Comment)
        .filter(Comment.thread_id == thread_id)
        .order_by(Comment.created_at)
        .all()
    )

    return comments