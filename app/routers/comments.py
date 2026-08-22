from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.discussion_thread import DiscussionThread
from app.schemas.comment import CommentCreate, CommentResponse
from app.core.security import get_current_user


# ============================================================
# Router for decision-related comment APIs
# ============================================================

decision_comments_router = APIRouter(
    prefix="/decisions",
    tags=["Comments"]
)


# ============================================================
# Router for individual comment APIs
# ============================================================

comments_router = APIRouter(
    prefix="/comments",
    tags=["Comments"]
)


# ============================================================
# CREATE COMMENT
# POST /decisions/{decision_id}/comments
# ============================================================

@decision_comments_router.post(
    "/{decision_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_comment(
    decision_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    new_comment = Comment(
        decision_id=decision_id,
        user_id=current_user.id,
        content=comment.content
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment


# ============================================================
# GET ALL COMMENTS FOR A DECISION
# GET /decisions/{decision_id}/comments
# ============================================================

@decision_comments_router.get(
    "/{decision_id}/comments",
    response_model=List[CommentResponse]
)
def get_comments(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return (
        db.query(Comment)
        .filter(Comment.decision_id == decision_id)
        .all()
    )


# ============================================================
# GET COMMENT BY ID
# GET /comments/{comment_id}
# ============================================================

@comments_router.get(
    "/{comment_id}",
    response_model=CommentResponse
)
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    existing_comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if not existing_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    return existing_comment


# ============================================================
# UPDATE OWN COMMENT
# PUT /comments/{comment_id}
# ============================================================

@comments_router.put(
    "/{comment_id}",
    response_model=CommentResponse
)
def update_comment(
    comment_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    existing_comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if not existing_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    if existing_comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own comments"
        )

    existing_comment.content = comment.content

    db.commit()
    db.refresh(existing_comment)

    return existing_comment


# ============================================================
# DELETE OWN COMMENT
# DELETE /comments/{comment_id}
# ============================================================

@comments_router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    existing_comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if not existing_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    if existing_comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments"
        )

    db.delete(existing_comment)
    db.commit()

    return None
# ============================================================
# CREATE REPLY TO DISCUSSION THREAD
# POST /comments/threads/{thread_id}/comments
# ============================================================

@comments_router.post(
    "/threads/{thread_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_thread_reply(
    thread_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    thread = (
        db.query(DiscussionThread)
        .filter(DiscussionThread.id == thread_id)
        .first()
    )

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found"
        )

    new_reply = Comment(
        decision_id=thread.decision_id,
        thread_id=thread_id,
        user_id=current_user.id,
        content=comment.content
    )

    db.add(new_reply)
    db.commit()
    db.refresh(new_reply)

    return new_reply