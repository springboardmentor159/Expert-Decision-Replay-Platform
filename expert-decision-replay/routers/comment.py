from fastapi import APIRouter, Depends, HTTPException, status
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
from app.core.audit_logger import create_audit_log


router = APIRouter(
    tags=["Comments"]
)


# =========================================================
# CREATE COMMENT
# =========================================================

@router.post(
    "/decisions/{decision_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_comment(
    decision_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # Check whether the decision exists
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

    # Create comment
    comment = Comment(
        decision_id=decision_id,
        user_id=current_user.id,
        content=comment_data.content
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    # =====================================================
    # AUTOMATIC AUDIT LOG - CREATE COMMENT
    # =====================================================

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Comment",
        entity_id=comment.id,
        description=f"Comment {comment.id} created for decision {decision_id}",
        new_value={
            "decision_id": comment.decision_id,
            "user_id": comment.user_id,
            "content": comment.content
        },
        request_method="POST",
        endpoint=f"/decisions/{decision_id}/comments"
    )

    return comment


# =========================================================
# GET ALL COMMENTS FOR A DECISION
# =========================================================

@router.get(
    "/decisions/{decision_id}/comments",
    response_model=list[CommentResponse]
)
def get_comments(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # Check whether the decision exists
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

    # Get all comments for this decision
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
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
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
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Only the user who created the comment can update it
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update this comment"
        )

    # Store old value before update
    old_content = comment.content

    comment.content = comment_data.content

    db.commit()
    db.refresh(comment)

    # =====================================================
    # AUTOMATIC AUDIT LOG - UPDATE COMMENT
    # =====================================================

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Comment",
        entity_id=comment.id,
        description=f"Comment {comment.id} updated",
        old_value={
            "content": old_content
        },
        new_value={
            "content": comment.content
        },
        request_method="PUT",
        endpoint=f"/comments/{comment_id}"
    )

    return comment


# =========================================================
# DELETE COMMENT
# =========================================================

@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Only the user who created the comment can delete it
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to delete this comment"
        )

    # Store old value before deletion
    old_value = {
        "decision_id": comment.decision_id,
        "user_id": comment.user_id,
        "content": comment.content
    }

    db.delete(comment)
    db.commit()

    # =====================================================
    # AUTOMATIC AUDIT LOG - DELETE COMMENT
    # =====================================================

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="Comment",
        entity_id=comment_id,
        description=f"Comment {comment_id} deleted",
        old_value=old_value,
        request_method="DELETE",
        endpoint=f"/comments/{comment_id}"
    )

    return None