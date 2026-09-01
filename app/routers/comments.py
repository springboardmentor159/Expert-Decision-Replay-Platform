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
    CommentResponse
)
from app.routers.auth import get_current_user


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
    current_user: User = Depends(get_current_user)
):
    # Check whether decision exists
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    # Create comment
    comment = Comment(
        decision_id=decision_id,
        user_id=current_user.id,
        content=comment_data.content
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


# =========================================================
# GET COMMENTS FOR A DECISION
# =========================================================

@router.get(
    "/decisions/{decision_id}/comments",
    response_model=list[CommentResponse]
)
def get_comments(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check whether decision exists
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    comments = db.query(Comment).filter(
        Comment.decision_id == decision_id
    ).order_by(
        Comment.created_at.asc()
    ).all()

    return comments


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

    # Ownership check
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update this comment"
        )

    # Only content can be changed
    comment.content = comment_data.content

    db.commit()
    db.refresh(comment)

    return comment


# =========================================================
# DELETE COMMENT
# =========================================================

@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT
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

    # Ownership check
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to delete this comment"
        )

    db.delete(comment)
    db.commit()

    return None

@router.post(
    "/threads/{thread_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_thread_reply(
    thread_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check whether thread exists
    thread = db.query(DiscussionThread).filter(
        DiscussionThread.id == thread_id
    ).first()

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found"
        )

    # Create reply
    reply = Comment(
        decision_id=thread.decision_id,
        thread_id=thread_id,
        user_id=current_user.id,
        content=comment_data.content
    )

    db.add(reply)
    db.commit()
    db.refresh(reply)

    return reply



@router.get(
    "/threads/{thread_id}/comments",
    response_model=list[CommentResponse]
)
def get_thread_replies(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check whether thread exists
    thread = db.query(DiscussionThread).filter(
        DiscussionThread.id == thread_id
    ).first()

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found"
        )

    replies = db.query(Comment).filter(
        Comment.thread_id == thread_id
    ).order_by(
        Comment.created_at.asc()
    ).all()

    return replies