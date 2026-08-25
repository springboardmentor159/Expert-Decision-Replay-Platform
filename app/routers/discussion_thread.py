from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.discussion_thread import DiscussionThread
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.discussion_thread import ThreadCreate, ThreadResponse, ThreadUpdate

router = APIRouter(
    prefix="/decisions",
    tags=["Threads"]
)

threads_router = APIRouter(
    prefix="/threads",
    tags=["Threads"]
)


def _get_decision_or_404(db: Session, decision_id: int) -> Decision:
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )
    return decision


def _get_thread_or_404(db: Session, thread_id: int) -> DiscussionThread:
    thread = db.query(DiscussionThread).filter(DiscussionThread.id == thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    return thread


@router.post(
    "/{decision_id}/threads",
    response_model=ThreadResponse,
    status_code=status.HTTP_201_CREATED
)
def create_thread(
    decision_id: int,
    thread_data: ThreadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _get_decision_or_404(db, decision_id)

    new_thread = DiscussionThread(
        decision_id=decision_id,
        created_by=current_user.id,
        title=thread_data.title,
        description=thread_data.description,
    )

    db.add(new_thread)
    db.commit()
    db.refresh(new_thread)

    return new_thread


@router.get(
    "/{decision_id}/threads",
    response_model=List[ThreadResponse]
)
def get_threads_by_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _get_decision_or_404(db, decision_id)

    threads = db.query(DiscussionThread).filter(
        DiscussionThread.decision_id == decision_id
    ).all()

    return threads


@threads_router.get(
    "/{thread_id}",
    response_model=ThreadResponse
)
def get_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return _get_thread_or_404(db, thread_id)


@threads_router.put(
    "/{thread_id}",
    response_model=ThreadResponse
)
def update_thread(
    thread_id: int,
    thread_data: ThreadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = _get_thread_or_404(db, thread_id)

    if thread.created_by != current_user.id and current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this thread"
        )

    if thread_data.title is not None:
        thread.title = thread_data.title
    if thread_data.description is not None:
        thread.description = thread_data.description
    if thread_data.status is not None:
        thread.status = thread_data.status

    thread.updated_at = func.now()

    db.commit()
    db.refresh(thread)

    return thread


@threads_router.delete(
    "/{thread_id}"
)
def delete_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = _get_thread_or_404(db, thread_id)

    if thread.created_by != current_user.id and current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this thread"
        )

    db.delete(thread)
    db.commit()

    return {"message": "Thread deleted successfully"}


@threads_router.post(
    "/{thread_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_thread_reply(
    thread_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = _get_thread_or_404(db, thread_id)

    new_comment = Comment(
        decision_id=thread.decision_id,
        user_id=current_user.id,
        thread_id=thread_id,
        content=comment_data.content,
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment
