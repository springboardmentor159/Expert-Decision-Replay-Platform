from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.decision import Decision
from app.models.comment import Comment
from app.models.discussion_thread import DiscussionThread
from app.services.activity import create_activity
from app.services.audit import create_audit_log
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
)


router = APIRouter(
    tags=["Comments"],
)


# ============================================================
# CREATE COMMENT
# ============================================================

@router.post(
    "/decisions/{decision_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    decision_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    new_comment = Comment(
        decision_id=decision_id,
        user_id=current_user.id,
        content=comment_data.content,
    )

    db.add(new_comment)
    db.flush()

    # Audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Comment",
        entity_id=new_comment.id,
        description=(
            f"User {current_user.id} created "
            f"Comment {new_comment.id}"
        ),
        new_value={
            "decision_id": decision_id,
            "user_id": current_user.id,
            "content": new_comment.content,
        },
        request_method="POST",
        endpoint=f"/decisions/{decision_id}/comments",
    )

    # Activity log
    create_activity(
        db=db,
        user_id=current_user.id,
        action="Comment created",
        entity_type="Comment",
        entity_id=new_comment.id,
        description=(
            f"User {current_user.id} added "
            f"Comment {new_comment.id}"
        ),
    )

    db.commit()
    db.refresh(new_comment)

    return new_comment


# ============================================================
# GET ALL COMMENTS FOR DECISION
# ============================================================

@router.get(
    "/decisions/{decision_id}/comments",
    response_model=List[CommentResponse],
)
def get_comments(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    return (
        db.query(Comment)
        .filter(Comment.decision_id == decision_id)
        .order_by(Comment.created_at.asc())
        .all()
    )


# ============================================================
# GET COMMENT BY ID
# ============================================================

@router.get(
    "/comments/{comment_id}",
    response_model=CommentResponse,
)
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    return comment


# ============================================================
# UPDATE COMMENT
# ============================================================

@router.put(
    "/comments/{comment_id}",
    response_model=CommentResponse,
)
def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    # Only owner can update
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to update this comment"
            ),
        )

    # Capture old value
    old_value = {
        "decision_id": comment.decision_id,
        "thread_id": comment.thread_id,
        "user_id": comment.user_id,
        "content": comment.content,
    }

    # Update content
    comment.content = comment_data.content

    db.flush()

    # Audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Comment",
        entity_id=comment.id,
        description=(
            f"User {current_user.id} updated "
            f"Comment {comment.id}"
        ),
        old_value=old_value,
        new_value={
            "decision_id": comment.decision_id,
            "thread_id": comment.thread_id,
            "user_id": comment.user_id,
            "content": comment.content,
        },
        request_method="PUT",
        endpoint=f"/comments/{comment.id}",
    )

    # Activity log
    create_activity(
        db=db,
        user_id=current_user.id,
        action="Comment updated",
        entity_type="Comment",
        entity_id=comment.id,
        description=(
            f"User {current_user.id} updated "
            f"Comment {comment.id}"
        ),
    )

    db.commit()
    db.refresh(comment)

    return comment


# ============================================================
# DELETE COMMENT
# ============================================================

@router.delete(
    "/comments/{comment_id}",
)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    # Only owner can delete
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to delete this comment"
            ),
        )

    # Capture values before deletion
    old_value = {
        "decision_id": comment.decision_id,
        "thread_id": comment.thread_id,
        "user_id": comment.user_id,
        "content": comment.content,
    }

    # Audit log BEFORE deletion
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="Comment",
        entity_id=comment.id,
        description=(
            f"User {current_user.id} deleted "
            f"Comment {comment.id}"
        ),
        old_value=old_value,
        request_method="DELETE",
        endpoint=f"/comments/{comment.id}",
    )

    # Activity log
    create_activity(
        db=db,
        user_id=current_user.id,
        action="Comment deleted",
        entity_type="Comment",
        entity_id=comment.id,
        description=(
            f"User {current_user.id} deleted "
            f"Comment {comment.id}"
        ),
    )

    db.delete(comment)
    db.commit()

    return {
        "message": "Comment deleted successfully"
    }


# ============================================================
# CREATE THREAD REPLY
# ============================================================

@router.post(
    "/threads/{thread_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_thread_reply(
    thread_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thread = (
        db.query(DiscussionThread)
        .filter(DiscussionThread.id == thread_id)
        .first()
    )

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found",
        )

    new_comment = Comment(
        decision_id=thread.decision_id,
        thread_id=thread.id,
        user_id=current_user.id,
        content=comment_data.content,
    )

    db.add(new_comment)
    db.flush()

    # Audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Comment",
        entity_id=new_comment.id,
        description=(
            f"User {current_user.id} replied to "
            f"DiscussionThread {thread.id}"
        ),
        new_value={
            "decision_id": thread.decision_id,
            "thread_id": thread.id,
            "user_id": current_user.id,
            "content": new_comment.content,
        },
        request_method="POST",
        endpoint=f"/threads/{thread_id}/comments",
    )

    # Activity log
    create_activity(
        db=db,
        user_id=current_user.id,
        action="Thread reply created",
        entity_type="Comment",
        entity_id=new_comment.id,
        description=(
            f"User {current_user.id} replied to "
            f"DiscussionThread {thread.id}"
        ),
    )

    db.commit()
    db.refresh(new_comment)

    return new_comment


# ============================================================
# GET ALL THREAD REPLIES
# ============================================================

@router.get(
    "/threads/{thread_id}/comments",
    response_model=List[CommentResponse],
)
def get_thread_replies(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thread = (
        db.query(DiscussionThread)
        .filter(DiscussionThread.id == thread_id)
        .first()
    )

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found",
        )

    return (
        db.query(Comment)
        .filter(Comment.thread_id == thread_id)
        .order_by(Comment.created_at.asc())
        .all()
    )