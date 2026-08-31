from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.enums import UserRole
from app.models.user import User
from app.services.activity import log_activity
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate

router = APIRouter(
    prefix="/decisions",
    tags=["Comments"]
)

comments_router = APIRouter(
    prefix="/comments",
    tags=["Comments"]
)


def _get_decision_or_404(db: Session, decision_id: int) -> Decision:
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )
    return decision


@router.post(
    "/{decision_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_comment(
    decision_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _get_decision_or_404(db, decision_id)

    new_comment = Comment(
        decision_id=decision_id,
        user_id=current_user.id,
        content=comment_data.content,
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    log_activity(
        db,
        current_user.id,
        "create",
        "comment",
        new_comment.id,
        f"Created comment on decision {decision_id}",
    )

    return new_comment


@router.get(
    "/{decision_id}/comments",
    response_model=List[CommentResponse]
)
def get_comments_by_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _get_decision_or_404(db, decision_id)

    comments = db.query(Comment).filter(
        Comment.decision_id == decision_id
    ).all()

    return comments


@comments_router.get(
    "/{comment_id}",
    response_model=CommentResponse
)
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    return comment


@comments_router.put(
    "/{comment_id}",
    response_model=CommentResponse
)
def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Ownership check: only author or Administrator can update
    if comment.user_id != current_user.id and current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this comment"
        )

    comment.content = comment_data.content
    comment.updated_at = func.now()

    db.commit()
    db.refresh(comment)

    log_activity(
        db,
        current_user.id,
        "update",
        "comment",
        comment.id,
        f"Updated comment {comment.id}",
    )

    return comment


@comments_router.delete(
    "/{comment_id}"
)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Ownership check: only author or Administrator can delete
    if comment.user_id != current_user.id and current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment"
        )

    db.delete(comment)
    db.commit()

    return {
        "message": "Comment deleted successfully"
    }
