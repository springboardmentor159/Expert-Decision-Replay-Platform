"""
Comment API router.

Endpoints:
    POST   /decisions/{decision_id}/comments              create a comment
    GET    /decisions/{decision_id}/comments              list comments for a decision
    GET    /comments/{comment_id}                         get a specific comment
    PUT    /comments/{comment_id}                         update own comment
    DELETE /comments/{comment_id}                         delete own comment
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.user import User
from app.services.activity import record_activity
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse

router = APIRouter(tags=["Comments"])


def _get_decision_or_404(db: Session, decision_id: int) -> Decision:
    """Get a decision or raise 404"""
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found"
        )
    return decision


def _get_comment_or_404(db: Session, comment_id: int) -> Comment:
    """Get a comment or raise 404"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    return comment


def _ensure_owner_or_privileged(comment: Comment, current_user: User) -> None:
    """Verify user owns the comment or has admin/manager role"""
    is_owner = comment.user_id == current_user.id
    is_privileged = current_user.role in {"admin", "manager"}
    if not (is_owner or is_privileged):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this comment",
        )


@router.post(
    "/decisions/{decision_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a comment on a decision",
)
def create_comment(
    decision_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a comment on a decision"""
    _get_decision_or_404(db, decision_id)

    comment = Comment(
        decision_id=decision_id,
        user_id=current_user.id,
        content=payload.content,
    )
    db.add(comment)
    db.flush()
    record_activity(db, current_user.id, "comment_created", "Comment", "Comment added", comment.id)
    db.commit()
    db.refresh(comment)
    return comment


@router.get(
    "/decisions/{decision_id}/comments",
    response_model=list[CommentResponse],
    summary="Get all comments for a decision",
)
def get_comments_for_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all comments for a specific decision"""
    _get_decision_or_404(db, decision_id)

    comments = (
        db.query(Comment)
        .filter(Comment.decision_id == decision_id, Comment.thread_id.is_(None))
        .order_by(Comment.created_at.asc())
        .all()
    )
    return comments


@router.get(
    "/comments/{comment_id}",
    response_model=CommentResponse,
    summary="Get a specific comment",
)
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific comment by ID"""
    return _get_comment_or_404(db, comment_id)


@router.put(
    "/comments/{comment_id}",
    response_model=CommentResponse,
    summary="Update a comment",
)
def update_comment(
    comment_id: int,
    payload: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a comment (only author or admin can update)"""
    comment = _get_comment_or_404(db, comment_id)
    _ensure_owner_or_privileged(comment, current_user)

    comment.content = payload.content
    db.commit()
    db.refresh(comment)
    return comment


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a comment",
)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a comment (only author or admin can delete)"""
    comment = _get_comment_or_404(db, comment_id)
    _ensure_owner_or_privileged(comment, current_user)
    
    db.delete(comment)
    db.commit()

    db.delete(comment)
    db.commit()
    return None


"""
Wire this router into your FastAPI app, e.g. in app/main.py:

    from app.routers import comments
    app.include_router(comments.router)
"""