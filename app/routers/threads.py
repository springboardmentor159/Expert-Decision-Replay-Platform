from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.discussion_thread import DiscussionThread
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.discussion_thread import (
    ThreadCreate,
    ThreadDetailResponse,
    ThreadResponse,
    ThreadUpdate,
)

from app.services.activity_logger import log_activity

router = APIRouter(tags=["Discussion Threads"])


@router.post(
    "/decisions/{decision_id}/threads",
    response_model=ThreadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new discussion thread for a decision"
)
def create_thread(
    decision_id: int,
    thread_in: ThreadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    new_thread = DiscussionThread(
        decision_id=decision_id,
        created_by=current_user.id,
        title=thread_in.title,
        description=thread_in.description,
        status="Open"
    )
    db.add(new_thread)
    db.commit()
    db.refresh(new_thread)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="create_thread",
        entity_type="thread",
        entity_id=new_thread.id,
        description=f"User {current_user.full_name} created discussion thread '{new_thread.title}' on decision '{decision.title}'"
    )

    return new_thread


@router.get(
    "/decisions/{decision_id}/threads",
    response_model=List[ThreadResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all discussion threads for a decision"
)
def get_threads_for_decision(
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

    threads = db.query(DiscussionThread).filter(DiscussionThread.decision_id == decision_id).order_by(DiscussionThread.created_at.desc()).all()
    return threads


@router.get(
    "/threads/{thread_id}",
    response_model=ThreadDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a discussion thread by ID including replies"
)
def get_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = db.query(DiscussionThread).filter(DiscussionThread.id == thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    return thread


@router.put(
    "/threads/{thread_id}",
    response_model=ThreadResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a discussion thread"
)
def update_thread(
    thread_id: int,
    thread_in: ThreadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = db.query(DiscussionThread).filter(DiscussionThread.id == thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )

    # Ownership / role check
    if thread.created_by != current_user.id and current_user.role not in ["Administrator", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this thread"
        )

    if thread_in.title is not None:
        thread.title = thread_in.title
    if thread_in.description is not None:
        thread.description = thread_in.description
    if thread_in.status is not None:
        thread.status = thread_in.status

    db.commit()
    db.refresh(thread)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="update_thread",
        entity_type="thread",
        entity_id=thread.id,
        description=f"User {current_user.full_name} updated discussion thread '{thread.title}'"
    )

    return thread


@router.delete(
    "/threads/{thread_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a discussion thread"
)
def delete_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = db.query(DiscussionThread).filter(DiscussionThread.id == thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )

    # Ownership / role check
    if thread.created_by != current_user.id and current_user.role not in ["Administrator", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this thread"
        )

    db.delete(thread)
    db.commit()
    return {"message": "Thread deleted successfully"}


@router.post(
    "/threads/{thread_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a reply to a discussion thread"
)
def create_thread_reply(
    thread_id: int,
    comment_in: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = db.query(DiscussionThread).filter(DiscussionThread.id == thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )

    new_reply = Comment(
        decision_id=thread.decision_id,
        thread_id=thread.id,
        user_id=current_user.id,
        content=comment_in.content
    )
    db.add(new_reply)
    db.commit()
    db.refresh(new_reply)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="create_thread_reply",
        entity_type="comment",
        entity_id=new_reply.id,
        description=f"User {current_user.full_name} replied to discussion thread '{thread.title}'"
    )

    return new_reply


@router.get(
    "/threads/{thread_id}/comments",
    response_model=List[CommentResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all replies for a discussion thread"
)
def get_thread_replies(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = db.query(DiscussionThread).filter(DiscussionThread.id == thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )

    replies = db.query(Comment).filter(Comment.thread_id == thread_id).order_by(Comment.created_at.asc()).all()
    return replies
