from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.user import User
from app.schemas.comment import (
    CommentCreate,
    CommentResponse,
    CommentUpdate
)
from app.services.auth import get_current_user


router = APIRouter(
    tags=["Comments"]
)


# Create a comment for a decision
@router.post(
    "/decisions/{decision_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_comment(
    decision_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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

    comment = Comment(
        decision_id=decision.id,
        user_id=current_user.id,
        content=comment_data.content
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


# Get all comments for a decision
@router.get(
    "/decisions/{decision_id}/comments",
    response_model=list[CommentResponse]
)
def get_decision_comments(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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

    comments = (
        db.query(Comment)
        .filter(Comment.decision_id == decision_id)
        .order_by(Comment.created_at)
        .all()
    )

    return comments


# Get a comment by ID
@router.get(
    "/comments/{comment_id}",
    response_model=CommentResponse
)
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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


# Update a comment
@router.put(
    "/comments/{comment_id}",
    response_model=CommentResponse
)
def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own comments"
        )

    comment.content = comment_data.content

    db.commit()
    db.refresh(comment)

    return comment


# Delete a comment
@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments"
        )

    db.delete(comment)
    db.commit()

    return None