from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user

from app.models.comment import Comment
from app.models.decision import Decision
from app.models.activity_log import ActivityLog

from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse
)


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

    user_id = int(current_user["sub"])

    # Check decision exists
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    # Create comment
    comment = Comment(
        decision_id=decision_id,
        user_id=user_id,
        content=comment_data.content
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    # -----------------------------------------------------
    # Sprint 10 Activity Log
    # -----------------------------------------------------

    log = ActivityLog(
        user_id=user_id,
        action="Comment Created",
        entity_type="Comment",
        entity_id=comment.id,
        description=f"Comment {comment.id} added to decision {decision_id}"
    )

    db.add(log)
    db.commit()

    return comment


# =========================================================
# GET COMMENTS FOR DECISION
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

    # Check decision exists
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    return (
        db.query(Comment)
        .filter(
            Comment.decision_id == decision_id,
            Comment.thread_id.is_(None)
        )
        .all()
    )


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
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    user_id = int(current_user["sub"])

    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    # Only the comment owner can update it
    if comment.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own comment"
        )

    comment.content = comment_data.content

    db.commit()
    db.refresh(comment)

    # -----------------------------------------------------
    # Sprint 10 Activity Log
    # -----------------------------------------------------

    log = ActivityLog(
        user_id=user_id,
        action="Comment Updated",
        entity_type="Comment",
        entity_id=comment.id,
        description=f"Comment {comment.id} updated"
    )

    db.add(log)
    db.commit()

    return comment


# =========================================================
# DELETE COMMENT
# =========================================================

@router.delete(
    "/comments/{comment_id}"
)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    user_id = int(current_user["sub"])

    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    # Only the comment owner can delete it
    if comment.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own comment"
        )

    # Save information before deleting
    comment_id_value = comment.id
    decision_id = comment.decision_id

    # Delete comment
    db.delete(comment)
    db.commit()

    # -----------------------------------------------------
    # Sprint 10 Activity Log
    # -----------------------------------------------------

    log = ActivityLog(
        user_id=user_id,
        action="Comment Deleted",
        entity_type="Comment",
        entity_id=comment_id_value,
        description=(
            f"Comment {comment_id_value} deleted "
            f"from decision {decision_id}"
        )
    )

    db.add(log)
    db.commit()

    return {
        "message": "Comment deleted successfully"
    }