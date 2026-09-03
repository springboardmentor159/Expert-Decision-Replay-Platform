"""
Discussion Thread API router.

Endpoints:
    POST   /decisions/{decision_id}/threads                create a thread
    GET    /decisions/{decision_id}/threads                list threads for a decision
    GET    /threads/{thread_id}                            get a specific thread
    PUT    /threads/{thread_id}                            update a thread
    DELETE /threads/{thread_id}                            delete a thread
    POST   /threads/{thread_id}/comments                   add a reply to a thread
    GET    /threads/{thread_id}/comments                   get replies to a thread
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.discussion_thread import DiscussionThread
from app.models.user import User
from app.services.activity import record_activity
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.discussion_thread import (
    DiscussionThreadCreate,
    DiscussionThreadUpdate,
    DiscussionThreadResponse,
)

router = APIRouter(tags=["Discussion Threads"])


def _get_decision_or_404(db: Session, decision_id: int) -> Decision:
    """Get a decision or raise 404"""
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found"
        )
    return decision


def _get_thread_or_404(db: Session, thread_id: int) -> DiscussionThread:
    """Get a discussion thread or raise 404"""
    thread = db.query(DiscussionThread).filter(DiscussionThread.id == thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Discussion thread not found"
        )
    return thread


def _ensure_owner_or_privileged(obj, current_user: User, owner_field: str = "created_by") -> None:
    """Verify user owns the object or has admin/manager role"""
    is_owner = getattr(obj, owner_field) == current_user.id
    is_privileged = current_user.role in {"admin", "manager"}
    if not (is_owner or is_privileged):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this resource",
        )


@router.post(
    "/decisions/{decision_id}/threads",
    response_model=DiscussionThreadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a discussion thread for a decision",
)
def create_thread(
    decision_id: int,
    payload: DiscussionThreadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new discussion thread for a decision"""
    _get_decision_or_404(db, decision_id)

    thread = DiscussionThread(
        decision_id=decision_id,
        created_by=current_user.id,
        title=payload.title,
        description=payload.description,
        status="Open",
    )
    db.add(thread)
    db.flush()
    record_activity(db, current_user.id, "discussion_thread_created", "DiscussionThread", "Discussion thread created", thread.id)
    db.commit()
    db.refresh(thread)
    return thread


@router.get(
    "/decisions/{decision_id}/threads",
    response_model=list[DiscussionThreadResponse],
    summary="Get all threads for a decision",
)
def get_threads_for_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all discussion threads for a specific decision"""
    _get_decision_or_404(db, decision_id)

    threads = (
        db.query(DiscussionThread)
        .filter(DiscussionThread.decision_id == decision_id)
        .order_by(DiscussionThread.created_at.asc())
        .all()
    )
    return threads


@router.get(
    "/threads/{thread_id}",
    response_model=DiscussionThreadResponse,
    summary="Get a specific discussion thread",
)
def get_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific discussion thread by ID"""
    return _get_thread_or_404(db, thread_id)


@router.put(
    "/threads/{thread_id}",
    response_model=DiscussionThreadResponse,
    summary="Update a discussion thread",
)
def update_thread(
    thread_id: int,
    payload: DiscussionThreadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a discussion thread (only creator or admin can update)"""
    thread = _get_thread_or_404(db, thread_id)
    _ensure_owner_or_privileged(thread, current_user)

    if payload.title is not None:
        thread.title = payload.title
    if payload.description is not None:
        thread.description = payload.description
    if payload.status is not None:
        thread.status = payload.status

    db.commit()
    db.refresh(thread)
    return thread


@router.delete(
    "/threads/{thread_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a discussion thread",
)
def delete_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a discussion thread (only creator or admin can delete)"""
    thread = _get_thread_or_404(db, thread_id)
    _ensure_owner_or_privileged(thread, current_user)

    db.delete(thread)
    db.commit()


@router.post(
    "/threads/{thread_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a reply to a thread",
)
def add_reply_to_thread(
    thread_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a reply/comment to a discussion thread"""
    thread = _get_thread_or_404(db, thread_id)

    comment = Comment(
        decision_id=thread.decision_id,
        thread_id=thread_id,
        user_id=current_user.id,
        content=payload.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get(
    "/threads/{thread_id}/comments",
    response_model=list[CommentResponse],
    summary="Get all replies to a thread",
)
def get_thread_replies(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all replies/comments for a specific discussion thread"""
    _get_thread_or_404(db, thread_id)

    replies = (
        db.query(Comment)
        .filter(Comment.thread_id == thread_id)
        .order_by(Comment.created_at.asc())
        .all()
    )
    return replies
