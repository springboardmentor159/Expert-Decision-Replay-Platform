from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.discussion_thread import DiscussionThread
from app.models.user import User

from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
)

from app.core.security import get_current_user

from app.services.activity_log import create_activity_log
from app.services.audit_log import create_audit_log
from app.services.access_log import create_access_log

from app.models.audit_action import AuditAction
from app.models.audit_entity import AuditEntityType


router = APIRouter(
    tags=["Comments"]
)


# ==========================================
# CREATE COMMENT FOR A DECISION
# ==========================================
@router.post(
    "/decisions/{decision_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    decision_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    new_comment = Comment(
        decision_id=decision_id,
        user_id=current_user.id,
        content=comment.content,
        thread_id=None,
    )

    db.add(new_comment)
    db.flush()

    # Activity log
    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="created",
        entity_type="comment",
        entity_id=new_comment.id,
        description=f"Created comment on decision: {decision.title}",
    )

    # Audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type=AuditEntityType.COMMENT,
        entity_id=new_comment.id,
        description=f"Created comment on decision: {decision.title}",
        new_value={
            "decision_id": decision_id,
            "user_id": current_user.id,
            "content": new_comment.content,
            "thread_id": None,
        },
        request_method="POST",
        endpoint=f"/decisions/{decision_id}/comments",
    )

    db.commit()
    db.refresh(new_comment)

    return new_comment


# ==========================================
# GET ALL TOP-LEVEL COMMENTS FOR A DECISION
# ==========================================
@router.get(
    "/decisions/{decision_id}/comments",
    response_model=List[CommentResponse],
)
def get_comments(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    comments = db.query(Comment).filter(
        Comment.decision_id == decision_id,
        Comment.thread_id.is_(None),
    ).all()

    # Access log
    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="Comment",
        resource_id=decision_id,
        action="LIST",
    )

    db.commit()

    return comments


# ==========================================
# CREATE COMMENT / REPLY FOR A THREAD
# ==========================================
@router.post(
    "/threads/{thread_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_thread_comment(
    thread_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thread = db.query(DiscussionThread).filter(
        DiscussionThread.id == thread_id
    ).first()

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found",
        )

    new_comment = Comment(
        decision_id=thread.decision_id,
        thread_id=thread.id,
        user_id=current_user.id,
        content=comment.content,
    )

    db.add(new_comment)
    db.flush()

    # Activity log
    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="created",
        entity_type="comment",
        entity_id=new_comment.id,
        description=f"Created reply in discussion thread: {thread.id}",
    )

    # Audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type=AuditEntityType.COMMENT,
        entity_id=new_comment.id,
        description=f"Created reply in discussion thread: {thread.id}",
        new_value={
            "decision_id": thread.decision_id,
            "thread_id": thread.id,
            "user_id": current_user.id,
            "content": new_comment.content,
        },
        request_method="POST",
        endpoint=f"/threads/{thread_id}/comments",
    )

    db.commit()
    db.refresh(new_comment)

    return new_comment


# ==========================================
# GET ALL COMMENTS / REPLIES FOR A THREAD
# ==========================================
@router.get(
    "/threads/{thread_id}/comments",
    response_model=List[CommentResponse],
)
def get_thread_comments(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thread = db.query(DiscussionThread).filter(
        DiscussionThread.id == thread_id
    ).first()

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found",
        )

    comments = db.query(Comment).filter(
        Comment.thread_id == thread_id
    ).all()

    # Access log
    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="Comment",
        resource_id=thread_id,
        action="LIST",
    )

    db.commit()

    return comments


# ==========================================
# GET COMMENT BY ID
# ==========================================
@router.get(
    "/comments/{comment_id}",
    response_model=CommentResponse,
)
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    # Access log
    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="Comment",
        resource_id=comment.id,
        action="VIEW",
    )

    db.commit()

    return comment


# ==========================================
# UPDATE COMMENT
# ==========================================
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
    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    # Only the creator can update the comment
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this comment",
        )

    # Save old value for audit
    old_value = {
        "content": comment.content,
    }

    comment.content = comment_data.content

    db.flush()

    # Activity log
    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="updated",
        entity_type="comment",
        entity_id=comment.id,
        description=f"Updated comment {comment.id}",
    )

    # Audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type=AuditEntityType.COMMENT,
        entity_id=comment.id,
        description=f"Updated comment {comment.id}",
        old_value=old_value,
        new_value={
            "content": comment.content,
        },
        request_method="PUT",
        endpoint=f"/comments/{comment_id}",
    )

    # Access log
    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="Comment",
        resource_id=comment.id,
        action="UPDATE",
    )

    db.commit()
    db.refresh(comment)

    return comment


# ==========================================
# DELETE COMMENT
# ==========================================
@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_200_OK,
)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    # Only the creator can delete the comment
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this comment",
        )

    # Save values before delete
    old_value = {
        "decision_id": comment.decision_id,
        "thread_id": comment.thread_id,
        "user_id": comment.user_id,
        "content": comment.content,
    }

    # Activity log
    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="deleted",
        entity_type="comment",
        entity_id=comment.id,
        description=f"Deleted comment {comment.id}",
    )

    # Audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.DELETE,
        entity_type=AuditEntityType.COMMENT,
        entity_id=comment.id,
        description=f"Deleted comment {comment.id}",
        old_value=old_value,
        request_method="DELETE",
        endpoint=f"/comments/{comment_id}",
    )

    # Access log
    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="Comment",
        resource_id=comment.id,
        action="DELETE",
    )

    db.delete(comment)
    db.commit()

    return {
        "message": "Comment deleted successfully"
    }