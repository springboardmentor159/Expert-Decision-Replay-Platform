from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.comment import Comment
from app.models.decision import Decision
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse
)


router = APIRouter(
    tags=["Comments"]
)


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
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    comment = Comment(
        decision_id=decision_id,
        user_id=int(current_user["sub"]),
        content=comment_data.content
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


@router.get(
    "/decisions/{decision_id}/comments",
    response_model=list[CommentResponse]
)
def get_comments(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    return db.query(Comment).filter(
        Comment.decision_id == decision_id,
        Comment.thread_id.is_(None)
    ).all()


@router.get(
    "/comments/{comment_id}",
    response_model=CommentResponse
)
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    return comment


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
    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    if comment.user_id != int(current_user["sub"]):
        raise HTTPException(
            status_code=403,
            detail="You can only update your own comment"
        )

    comment.content = comment_data.content

    db.commit()
    db.refresh(comment)

    return comment


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    if comment.user_id != int(current_user["sub"]):
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own comment"
        )

    db.delete(comment)
    db.commit()

    return {
        "message": "Comment deleted successfully"
    }