from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.user import User
from app.models.discussion_thread import DiscussionThread
from app.schemas.comment import CommentCreate, CommentResponse
from app.services.activity_service import log_activity
from app.services.audit_service import log_audit


router = APIRouter(
    tags=["Comments"]
)


# ---------------------------------------------------------
# CREATE COMMENT
# POST /threads/{thread_id}/comments
# ---------------------------------------------------------
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

    new_comment = Comment(
        decision_id=thread.decision_id,
        thread_id=thread_id,
        user_id=current_user.id,
        content=comment_data.content
    )

    db.add(new_comment)
    db.flush()

    log_activity(
        db,
        user_id=current_user.id,
        action="comment_created",
        entity_type="comment",
        entity_id=new_comment.id,
        description=f"User {current_user.id} added Comment {new_comment.id}"
    )

    log_audit(
        db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Comment",
        entity_id=new_comment.id,
        description=f"User {current_user.id} created Comment {new_comment.id}",
        new_value={
            "thread_id": thread_id,
            "decision_id": thread.decision_id,
        },
    )

    db.commit()
    db.refresh(new_comment)

    return new_comment


# ---------------------------------------------------------
# GET COMMENTS FOR A THREAD
# GET /threads/{thread_id}/comments
# ---------------------------------------------------------
@router.get(
    "/threads/{thread_id}/comments",
    response_model=List[CommentResponse]
)
def get_thread_comments(
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
        .order_by(Comment.created_at.asc())
        .all()
    )

    return comments