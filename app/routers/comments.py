from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.services.activity_logger import log_activity

router = APIRouter(tags=["Comments"])


@router.post(
    "/decisions/{decision_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a comment to a decision"
)
def create_comment(
    decision_id: int,
    comment_in: CommentCreate,
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

    log_activity(
        db=db,
        user_id=current_user.id,
        action="create",
        entity_type="Comment",
        entity_id=new_comment.id,
        description=f"User {current_user.full_name} added a comment on Decision #{decision_id}"
    )

    return new_comment


@router.get(
    "/decisions/{decision_id}/comments",
    response_model=List[CommentResponse],
    status_code=status.HTTP_200_OK,
    summary="Get comments for a decision"
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

    comments = db.query(Comment).filter(
        Comment.decision_id == decision_id,
        Comment.thread_id.is_(None)
    ).all()
    return comments


@router.get(
    "/comments/{comment_id}",
    response_model=CommentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get comment by ID"
)
def get_comment_by_id(
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
    summary="Update a comment"
)
def update_comment(
    comment_id: int,
    comment_in: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    if comment.user_id != current_user.id and current_user.role not in ["Administrator", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this comment"
        )

    comment.content = comment_in.content
    db.commit()
    db.refresh(comment)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="update",
        entity_type="Comment",
        entity_id=comment.id,
        description=f"User {current_user.full_name} updated comment #{comment.id}"
    )

    return comment


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a comment"
)
def delete_comment(
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

    if comment.user_id != current_user.id and current_user.role not in ["Administrator", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment"
        )

    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted successfully"}
