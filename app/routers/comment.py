
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.comment import Comment
from app.models.decision import Decision
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
)
from app.core.dependencies import get_current_user
from app.services.activity_log_service import create_activity_log
from app.services.audit_log_service import create_audit_log


router = APIRouter(
    tags=["Comments"],
    dependencies=[Depends(get_current_user)]
)


# =========================================================
# CREATE COMMENT
# =========================================================

@router.post(
    "/decisions/{decision_id}/comments",
    response_model=CommentResponse,
    status_code=201
)
def create_comment(
    decision_id: int,
    comment_data: CommentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
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

    user_id = int(current_user["sub"])

    new_comment = Comment(
        decision_id=decision_id,
        user_id=user_id,
        content=comment_data.content
    )

    db.add(new_comment)
    db.flush()

    # Activity log
    create_activity_log(
        db=db,
        user_id=user_id,
        action="CREATE",
        entity_type="Comment",
        entity_id=new_comment.id,
        description=f"Created comment on decision {decision_id}",
    )

    # Audit log
    create_audit_log(
        db=db,
        user_id=user_id,
        action="CREATE",
        entity_type="Comment",
        entity_id=new_comment.id,
        description=f"Created comment on decision {decision_id}",
        new_value={
            "decision_id": decision_id,
            "content": comment_data.content,
        },
        ip_address=request.client.host if request.client else None,
        request_method=request.method,
        endpoint=request.url.path,
    )

    db.commit()
    db.refresh(new_comment)

    return new_comment


# =========================================================
# GET ALL COMMENTS FOR A DECISION
# =========================================================

@router.get(
    "/decisions/{decision_id}/comments",
    response_model=List[CommentResponse]
)
def get_comments(
    decision_id: int,
    db: Session = Depends(get_db)
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

    comments = (
        db.query(Comment)
        .filter(Comment.decision_id == decision_id)
        .all()
    )

    return comments


# =========================================================
# GET COMMENT BY ID
# =========================================================

@router.get(
    "/comments/{comment_id}",
    response_model=CommentResponse
)
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db)
):
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    return comment


# =========================================================
# UPDATE COMMENT
# =========================================================

@router.put(
    "/comments/{comment_id}",
    response_model=CommentResponse
)
def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    user_id = int(current_user["sub"])

    if comment.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to update this comment"
        )

    old_value = {
        "decision_id": comment.decision_id,
        "content": comment.content,
    }

    comment.content = comment_data.content

    new_value = {
        "decision_id": comment.decision_id,
        "content": comment.content,
    }

    # Activity log
    create_activity_log(
        db=db,
        user_id=user_id,
        action="UPDATE",
        entity_type="Comment",
        entity_id=comment.id,
        description=f"Updated comment on decision {comment.decision_id}",
    )

    # Audit log
    create_audit_log(
        db=db,
        user_id=user_id,
        action="UPDATE",
        entity_type="Comment",
        entity_id=comment.id,
        description=f"Updated comment on decision {comment.decision_id}",
        old_value=old_value,
        new_value=new_value,
        ip_address=request.client.host if request.client else None,
        request_method=request.method,
        endpoint=request.url.path,
    )

    db.commit()
    db.refresh(comment)

    return comment


# =========================================================
# DELETE COMMENT
# =========================================================

@router.delete(
    "/comments/{comment_id}"
)
def delete_comment(
    comment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    user_id = int(current_user["sub"])

    if comment.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to delete this comment"
        )

    old_value = {
        "decision_id": comment.decision_id,
        "content": comment.content,
    }

    # Audit log must be created before deleting the comment.
    create_audit_log(
        db=db,
        user_id=user_id,
        action="DELETE",
        entity_type="Comment",
        entity_id=comment.id,
        description=f"Deleted comment from decision {comment.decision_id}",
        old_value=old_value,
        ip_address=request.client.host if request.client else None,
        request_method=request.method,
        endpoint=request.url.path,
    )

    # Activity log
    create_activity_log(
        db=db,
        user_id=user_id,
        action="DELETE",
        entity_type="Comment",
        entity_id=comment.id,
        description=f"Deleted comment from decision {comment.decision_id}",
    )

    db.delete(comment)
    db.commit()

    return {
        "message": "Comment deleted successfully"
    }
