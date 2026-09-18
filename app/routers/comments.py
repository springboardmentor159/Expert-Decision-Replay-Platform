from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.user import User
from app.schemas.audit_log import AuditAction, AuditEntityType
from app.schemas.comment import CommentCreate, CommentResponse
from app.services.activity_service import log_activity
from app.services.audit_service import log_audit


router = APIRouter(
    prefix="/decisions",
    tags=["Comments"],
)


ALLOWED_ROLES = {
    "Employee",
    "Reviewer",
    "Manager",
    "Administrator",
}


def get_decision_or_404(
    decision_id: int,
    db: Session,
) -> Decision:
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

    return decision


def ensure_decision_view_access(
    decision: Decision,
    current_user: User,
) -> None:
    role = str(current_user.role)

    if role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this decision",
        )

    if role == "Employee" and decision.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this decision",
        )


def get_comment_or_404(
    comment_id: int,
    db: Session,
) -> Comment:
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


def validate_comment_content(content: str) -> str:
    if not isinstance(content, str):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Comment content must be a string",
        )

    cleaned_content = content.strip()

    if not cleaned_content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Comment content cannot be empty",
        )

    return cleaned_content


# CREATE COMMENT
@router.post(
    "/{decision_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    decision_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        decision_id=decision_id,
        db=db,
    )

    ensure_decision_view_access(
        decision=decision,
        current_user=current_user,
    )

    content = validate_comment_content(
        comment_data.content
    )

    comment = Comment(
        decision_id=decision_id,
        user_id=current_user.id,
        content=content,
    )

    db.add(comment)
    db.flush()

    description = (
        f"User {current_user.id} created "
        f"Comment {comment.id} for Decision {decision_id}"
    )

    log_audit(
        db=db,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type=AuditEntityType.COMMENT,
        entity_id=comment.id,
        description=description,
        new_value={
            "decision_id": decision_id,
            "content": comment.content,
        },
        request_method="POST",
        endpoint=f"/decisions/{decision_id}/comments",
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Comment",
        entity_id=comment.id,
        description=description,
    )

    db.commit()
    db.refresh(comment)

    return comment


# GET ALL COMMENTS FOR A DECISION
@router.get(
    "/{decision_id}/comments",
    response_model=list[CommentResponse],
)
def get_comments(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        decision_id=decision_id,
        db=db,
    )

    ensure_decision_view_access(
        decision=decision,
        current_user=current_user,
    )

    return (
        db.query(Comment)
        .filter(Comment.decision_id == decision_id)
        .order_by(Comment.created_at.asc())
        .all()
    )


# UPDATE COMMENT
@router.put(
    "/comments/{comment_id}",
    response_model=CommentResponse,
)
def update_comment(
    comment_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = get_comment_or_404(
        comment_id=comment_id,
        db=db,
    )

    decision = get_decision_or_404(
        decision_id=comment.decision_id,
        db=db,
    )

    ensure_decision_view_access(
        decision=decision,
        current_user=current_user,
    )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own comment",
        )

    content = validate_comment_content(
        comment_data.content
    )

    old_content = comment.content
    comment.content = content

    description = (
        f"User {current_user.id} updated "
        f"Comment {comment.id}"
    )

    log_audit(
        db=db,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type=AuditEntityType.COMMENT,
        entity_id=comment.id,
        description=description,
        old_value={
            "decision_id": comment.decision_id,
            "content": old_content,
        },
        new_value={
            "decision_id": comment.decision_id,
            "content": comment.content,
        },
        request_method="PUT",
        endpoint=f"/decisions/comments/{comment.id}",
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Comment",
        entity_id=comment.id,
        description=description,
    )

    db.commit()
    db.refresh(comment)

    return comment


# DELETE COMMENT
@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_200_OK,
)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = get_comment_or_404(
        comment_id=comment_id,
        db=db,
    )

    decision = get_decision_or_404(
        decision_id=comment.decision_id,
        db=db,
    )

    ensure_decision_view_access(
        decision=decision,
        current_user=current_user,
    )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comment",
        )

    old_content = comment.content

    description = (
        f"User {current_user.id} deleted "
        f"Comment {comment.id}"
    )

    log_audit(
        db=db,
        user_id=current_user.id,
        action=AuditAction.DELETE,
        entity_type=AuditEntityType.COMMENT,
        entity_id=comment.id,
        description=description,
        old_value={
            "decision_id": comment.decision_id,
            "content": old_content,
        },
        request_method="DELETE",
        endpoint=f"/decisions/comments/{comment.id}",
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="Comment",
        entity_id=comment.id,
        description=description,
    )

    db.delete(comment)
    db.commit()

    return {
        "message": "Comment deleted successfully",
    }