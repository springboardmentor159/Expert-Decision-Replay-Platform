from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.audit import AuditAction
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.user import User, UserRole
from app.schemas.comment import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
)
from app.services.audit import create_audit_log
from app.services.auth import get_current_user


router = APIRouter(
    tags=["Comments"]
)


# DECISION ACCESS HELPERS
def get_decision_or_404(
    decision_id: int,
    db: Session,
    current_user: User,
) -> Decision:
    """
    Get a decision only if it belongs to
    the current user's organization.
    """

    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    # Organization isolation
    if decision.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    return decision


def can_access_decision(
    decision: Decision,
    current_user: User,
) -> bool:
    """
    User can access a decision only when:
    - The decision belongs to their organization, and
    - They are the creator, Reviewer, Manager, or Administrator.
    """

    if decision.organization_id != current_user.organization_id:
        return False

    return (
        decision.created_by == current_user.id
        or current_user.role in (
            UserRole.REVIEWER,
            UserRole.MANAGER,
            UserRole.ADMINISTRATOR,
        )
    )



# CREATE COMMENT FOR A DECISION
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
    decision = get_decision_or_404(
        decision_id,
        db,
        current_user,
    )

    if not can_access_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission to "
                "comment on this decision"
            ),
        )

    comment = Comment(
        decision_id=decision.id,
        user_id=current_user.id,
        content=comment_data.content,
    )

    db.add(comment)
    db.flush()

    create_audit_log(
        db=db,
        decision_id=decision.id,
        user_id=current_user.id,
        action=AuditAction.COMMENT_ADDED,
        entity_type="Comment",
        entity_id=comment.id,
        description=(
            f"Comment was added to decision "
            f"'{decision.title}'"
        ),
    )

    db.commit()
    db.refresh(comment)

    return comment


# GET ALL COMMENTS FOR A DECISION
@router.get(
    "/decisions/{decision_id}/comments",
    response_model=list[CommentResponse],
)
def get_decision_comments(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        decision_id,
        db,
        current_user,
    )

    if not can_access_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission to view "
                "comments for this decision"
            ),
        )

    comments = (
        db.query(Comment)
        .filter(
            Comment.decision_id == decision_id
        )
        .order_by(Comment.created_at)
        .all()
    )

    return comments


# GET COMMENT BY ID
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

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    decision = get_decision_or_404(
        comment.decision_id,
        db,
        current_user,
    )

    if not can_access_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this comment",
        )

    return comment


# UPDATE COMMENT
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

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    decision = get_decision_or_404(
        comment.decision_id,
        db,
        current_user,
    )

    if not can_access_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this comment",
        )

    # Only the comment author can update the comment.
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own comments",
        )

    comment.content = comment_data.content

    create_audit_log(
        db=db,
        decision_id=comment.decision_id,
        user_id=current_user.id,
        action=AuditAction.COMMENT_UPDATED,
        entity_type="Comment",
        entity_id=comment.id,
        description="Comment was updated",
    )

    db.commit()
    db.refresh(comment)

    return comment


# DELETE COMMENT
@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
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

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    decision = get_decision_or_404(
        comment.decision_id,
        db,
        current_user,
    )

    if not can_access_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this comment",
        )

    # Only the comment author can delete the comment.
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments",
        )

    decision_id = comment.decision_id

    create_audit_log(
        db=db,
        decision_id=decision_id,
        user_id=current_user.id,
        action=AuditAction.DELETE,
        entity_type="Comment",
        entity_id=comment.id,
        description="Comment was deleted",
    )

    db.delete(comment)
    db.commit()

    return None
