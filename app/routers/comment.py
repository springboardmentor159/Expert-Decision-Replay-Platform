from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.discussion_thread import DiscussionThread
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
)
from app.routers.users import get_current_user
from app.utils.activity_logger import log_activity


router = APIRouter(
    tags=["Comments"]
)


# CREATE COMMENT
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
        user_id=int(current_user["sub"]),
        content=comment_data.content
    )

    db.add(new_comment)
    db.flush()
    log_activity(db, int(current_user["sub"]), "comment_created", "Comment", new_comment.id, f"Comment {new_comment.id} added")
    db.commit()
    db.refresh(new_comment)

    return new_comment


# GET ALL COMMENTS FOR A DECISION
@router.get(
    "/decisions/{decision_id}/comments",
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


# GET COMMENT BY ID
@router.get(
    "/comments/{comment_id}",
    response_model=CommentResponse
)
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    return comment


# UPDATE COMMENT
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
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    current_user_id = int(current_user["sub"])

    if comment.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own comment"
        )

    comment.content = comment_data.content

    log_activity(db, current_user_id, "comment_updated", "Comment", comment.id, f"Comment {comment.id} updated")
    db.commit()
    db.refresh(comment)

    return comment


# DELETE COMMENT
@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id)
        .first()
    )

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    current_user_id = int(current_user["sub"])

    if comment.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comment"
        )

    db.delete(comment)
    db.commit()

    return None
# CREATE REPLY TO A DISCUSSION THREAD
@router.post(
    "/threads/{thread_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_thread_reply(
    thread_id: int,
    comment_data: CommentCreate,
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

    new_comment = Comment(
        decision_id=thread.decision_id,
        thread_id=thread_id,
        user_id=int(current_user["sub"]),
        content=comment_data.content
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment