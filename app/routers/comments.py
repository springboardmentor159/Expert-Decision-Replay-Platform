from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.services.activity_logger import log_activity
from app.services.audit_service import log_audit

router = APIRouter(tags=["Comments"])


@router.post(
    "/decisions/{decision_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a comment to a decision (Automatic Audit Logging)"
)
def create_comment(
    decision_id: int,
    comment_in: CommentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    new_comment = Comment(
        decision_id=decision_id,
        user_id=current_user.id,
        content=comment_in.content
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    client_ip = request.client.host if request.client else None
    log_audit(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Comment",
        entity_id=new_comment.id,
        description=f"Comment added to decision '{decision.title}'",
        ip_address=client_ip,
        old_value=None,
        new_value={"decision_id": decision_id, "content": new_comment.content},
        request_method="POST",
        endpoint=f"/decisions/{decision_id}/comments"
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="create_comment",
        entity_type="comment",
        entity_id=new_comment.id,
        description=f"User {current_user.full_name} added a comment to decision '{decision.title}'"
    )

    return new_comment


@router.get(
    "/decisions/{decision_id}/comments",
    response_model=List[CommentResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all comments for a decision"
)
def get_comments_for_decision(
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

    comments = db.query(Comment).filter(Comment.decision_id == decision_id).order_by(Comment.created_at.asc()).all()
    return comments


@router.get(
    "/comments/{comment_id}",
    response_model=CommentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a comment by ID"
)
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    return comment


@router.put(
    "/comments/{comment_id}",
    response_model=CommentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a comment (Automatic Audit Diff)"
)
def update_comment(
    comment_id: int,
    comment_in: CommentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Ownership / authorization check: only comment author or Admin/Manager can update
    if comment.user_id != current_user.id and current_user.role not in ["Administrator", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this comment"
        )

    old_snapshot = {"content": comment.content}
    comment.content = comment_in.content
    db.commit()
    db.refresh(comment)
    new_snapshot = {"content": comment.content}

    client_ip = request.client.host if request.client else None
    log_audit(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Comment",
        entity_id=comment.id,
        description=f"Comment {comment.id} updated",
        ip_address=client_ip,
        old_value=old_snapshot,
        new_value=new_snapshot,
        request_method="PUT",
        endpoint=f"/comments/{comment.id}"
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="update_comment",
        entity_type="comment",
        entity_id=comment.id,
        description=f"User {current_user.full_name} updated comment {comment.id}"
    )

    return comment


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a comment (Automatic Audit Logging)"
)
def delete_comment(
    comment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Ownership / authorization check: only comment author or Admin/Manager can delete
    if comment.user_id != current_user.id and current_user.role not in ["Administrator", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this comment"
        )

    old_snapshot = {"id": comment.id, "decision_id": comment.decision_id, "content": comment.content}

    client_ip = request.client.host if request.client else None
    log_audit(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="Comment",
        entity_id=comment.id,
        description=f"Comment {comment.id} deleted",
        ip_address=client_ip,
        old_value=old_snapshot,
        new_value=None,
        request_method="DELETE",
        endpoint=f"/comments/{comment.id}"
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="delete_comment",
        entity_type="comment",
        entity_id=comment.id,
        description=f"User {current_user.full_name} deleted comment {comment.id}"
    )

    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted successfully"}
