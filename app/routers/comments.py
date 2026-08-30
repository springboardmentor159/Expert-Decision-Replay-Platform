from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.discussion_thread import DiscussionThread
from app.models.user import User
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
)
from app.core.security import get_current_user


router = APIRouter(
    tags=["Comments"]
)


# ==========================================
# CREATE COMMENT FOR A DECISION
# ==========================================
@router.post(
    "/decisions/{decision_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    decision_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    new_comment = Comment(
        decision_id=decision_id,
        user_id=current_user.id,
        content=comment.content,
        thread_id=None,
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment


# ==========================================
# GET ALL TOP-LEVEL COMMENTS FOR A DECISION
# ==========================================
@router.get(
    "/decisions/{decision_id}/comments",
    response_model=List[CommentResponse],
)
def get_comments(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    return db.query(Comment).filter(
        Comment.decision_id == decision_id,
        Comment.thread_id.is_(None),
    ).all()


# ==========================================
# CREATE COMMENT / REPLY FOR A THREAD
# ==========================================
@router.post(
    "/threads/{thread_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_thread_comment(
    thread_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thread = db.query(DiscussionThread).filter(
        DiscussionThread.id == thread_id
    ).first()

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found",
        )

    new_comment = Comment(
        decision_id=thread.decision_id,
        thread_id=thread.id,
        user_id=current_user.id,
        content=comment.content,
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment


# ==========================================
# GET ALL COMMENTS / REPLIES FOR A THREAD
# ==========================================
@router.get(
    "/threads/{thread_id}/comments",
    response_model=List[CommentResponse],
)
def get_thread_comments(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thread = db.query(DiscussionThread).filter(
        DiscussionThread.id == thread_id
    ).first()

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found",
        )

    return db.query(Comment).filter(
        Comment.thread_id == thread_id
    ).all()


# ==========================================
# GET COMMENT BY ID
# ==========================================
@router.get(
    "/comments/{comment_id}",
    response_model=CommentResponse,
)
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    return comment


# ==========================================
# UPDATE COMMENT
# ==========================================
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
    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    # Only the creator can update the comment
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this comment",
        )

    comment.content = comment_data.content

    db.commit()
    db.refresh(comment)

    return comment


# ==========================================
# DELETE COMMENT
# ==========================================
@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_200_OK,
)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    # Only the creator can delete the comment
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this comment",
        )

    db.delete(comment)
    db.commit()

    return {
        "message": "Comment deleted successfully"
    }