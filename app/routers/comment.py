from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user

from app.models.decision import Decision
from app.models.comment import Comment

from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
)

from app.services.activity import create_activity_log
from app.services.audit import create_audit_log


router = APIRouter(
    tags=["Comments"],
)


# ---------------------------------------------------------
# CREATE COMMENT
# ---------------------------------------------------------
@router.post(
    "/decisions/{decision_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    decision_id: int,
    comment_data: CommentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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

    comment = Comment(
        decision_id=decision_id,
        user_id=current_user.id,
        content=comment_data.content,
    )

    db.add(comment)
    db.flush()

    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="created",
        entity_type="Comment",
        entity_id=comment.id,
        description=(
            f"User {current_user.id} added "
            f"Comment {comment.id} to Decision {decision_id}"
        ),
    )

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Comment",
        entity_id=comment.id,
        decision_id=decision_id,
        description=(
            f"Comment {comment.id} created "
            f"for Decision {decision_id}"
        ),
        ip_address=request.client.host if request.client else None,
        new_value={
            "id": comment.id,
            "decision_id": comment.decision_id,
            "user_id": comment.user_id,
            "content": comment.content,
        },
        request_method=request.method,
        endpoint=request.url.path,
    )

    db.commit()
    db.refresh(comment)

    return comment


# ---------------------------------------------------------
# GET COMMENTS
# ---------------------------------------------------------
@router.get(
    "/decisions/{decision_id}/comments",
    response_model=List[CommentResponse],
)
def get_decision_comments(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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
        .all()
    )


# ---------------------------------------------------------
# GET COMMENT
# ---------------------------------------------------------
@router.get(
    "/comments/{comment_id}",
    response_model=CommentResponse,
)
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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


# ---------------------------------------------------------
# UPDATE COMMENT
# ---------------------------------------------------------
@router.put(
    "/comments/{comment_id}",
    response_model=CommentResponse,
)
def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own comment",
        )

    old_value = {
        "id": comment.id,
        "decision_id": comment.decision_id,
        "user_id": comment.user_id,
        "content": comment.content,
    }

    comment.content = comment_data.content

    db.flush()

    new_value = {
        "id": comment.id,
        "decision_id": comment.decision_id,
        "user_id": comment.user_id,
        "content": comment.content,
    }

    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="updated",
        entity_type="Comment",
        entity_id=comment.id,
        description=(
            f"User {current_user.id} updated "
            f"Comment {comment.id}"
        ),
    )

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Comment",
        entity_id=comment.id,
        decision_id=comment.decision_id,
        description=f"Comment {comment.id} updated",
        ip_address=request.client.host if request.client else None,
        old_value=old_value,
        new_value=new_value,
        request_method=request.method,
        endpoint=request.url.path,
    )

    db.commit()
    db.refresh(comment)

    return comment


# ---------------------------------------------------------
# DELETE COMMENT
# ---------------------------------------------------------
@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_comment(
    comment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comment",
        )

    old_value = {
        "id": comment.id,
        "decision_id": comment.decision_id,
        "user_id": comment.user_id,
        "content": comment.content,
    }

    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="deleted",
        entity_type="Comment",
        entity_id=comment.id,
        description=(
            f"User {current_user.id} deleted "
            f"Comment {comment.id}"
        ),
    )

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="Comment",
        entity_id=comment.id,
        decision_id=comment.decision_id,
        description=f"Comment {comment.id} deleted",
        ip_address=request.client.host if request.client else None,
        old_value=old_value,
        request_method=request.method,
        endpoint=request.url.path,
    )

    db.delete(comment)
    db.commit()

    return None