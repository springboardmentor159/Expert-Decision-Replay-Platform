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

from app.core.security import get_current_user

from app.services.audit import log_audit


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    tags=["Comments"]
)


# =========================================================
# HELPER - COMMENT TO DICTIONARY
# =========================================================

def comment_to_dict(comment: Comment):
    """
    Convert Comment SQLAlchemy object into a dictionary
    suitable for storing inside audit_logs JSON fields.

    Only non-sensitive comment information is recorded.
    Passwords, JWTs and other credentials are never logged.
    """

    return {
        "id": comment.id,
        "decision_id": comment.decision_id,
        "thread_id": comment.thread_id,
        "user_id": comment.user_id,
        "content": comment.content
    }


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
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # -----------------------------------------------------
    # CHECK DECISION
    # -----------------------------------------------------

    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    # -----------------------------------------------------
    # CREATE COMMENT
    # -----------------------------------------------------

    new_comment = Comment(
        decision_id=decision_id,
        user_id=current_user.id,
        content=comment.content
    )

    db.add(new_comment)

    # Generate comment ID before audit record.
    db.flush()

    # -----------------------------------------------------
    # AUDIT - CREATE COMMENT
    # -----------------------------------------------------

    log_audit(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Comment",
        entity_id=new_comment.id,
        description=(
            f"User {current_user.id} created "
            f"Comment {new_comment.id} "
            f"for Decision {decision_id}"
        ),
        new_value=comment_to_dict(new_comment),
        request_method="POST",
        endpoint=f"/decisions/{decision_id}/comments"
    )

    # -----------------------------------------------------
    # COMMIT
    # -----------------------------------------------------

    db.commit()
    db.refresh(new_comment)

    return new_comment


# =========================================================
# GET ALL COMMENTS FOR A DECISION
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

    # -----------------------------------------------------
    # CHECK DECISION
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # FIND COMMENT
    # -----------------------------------------------------

    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # -----------------------------------------------------
    # AUTHORIZATION
    # -----------------------------------------------------

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update this comment"
        )

    # -----------------------------------------------------
    # SAVE OLD VALUE
    # -----------------------------------------------------

    old_value = comment_to_dict(comment)

    # -----------------------------------------------------
    # UPDATE
    # -----------------------------------------------------

    comment.content = comment_data.content

    db.flush()

    # -----------------------------------------------------
    # SAVE NEW VALUE
    # -----------------------------------------------------

    new_value = comment_to_dict(comment)

    # -----------------------------------------------------
    # AUDIT - UPDATE COMMENT
    # -----------------------------------------------------

    log_audit(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Comment",
        entity_id=comment.id,
        description=(
            f"User {current_user.id} updated "
            f"Comment {comment.id}"
        ),
        old_value=old_value,
        new_value=new_value,
        request_method="PUT",
        endpoint=f"/comments/{comment_id}"
    )

    # -----------------------------------------------------
    # COMMIT
    # -----------------------------------------------------

    db.commit()
    db.refresh(comment)

    return comment


# =========================================================
# DELETE COMMENT
# =========================================================

@router.delete(
    "/comments/{comment_id}"
)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # -----------------------------------------------------
    # FIND COMMENT
    # -----------------------------------------------------

    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # -----------------------------------------------------
    # AUTHORIZATION
    # -----------------------------------------------------

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to delete this comment"
        )

    # -----------------------------------------------------
    # SAVE OLD VALUE
    # -----------------------------------------------------

    old_value = comment_to_dict(comment)

    decision_id = comment.decision_id

    # -----------------------------------------------------
    # AUDIT - DELETE COMMENT
    # -----------------------------------------------------

    log_audit(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="Comment",
        entity_id=comment.id,
        description=(
            f"User {current_user.id} deleted "
            f"Comment {comment.id}"
        ),
        old_value=old_value,
        request_method="DELETE",
        endpoint=f"/comments/{comment_id}"
    )

    # -----------------------------------------------------
    # DELETE
    # -----------------------------------------------------

    db.delete(comment)

    db.commit()

    return {
        "message": "Comment deleted successfully",
        "comment_id": comment_id,
        "decision_id": decision_id
    }


# =========================================================
# CREATE REPLY FOR DISCUSSION THREAD
# =========================================================

@router.post(
    "/threads/{thread_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_thread_reply(
    thread_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # -----------------------------------------------------
    # CHECK THREAD
    # -----------------------------------------------------

    thread = db.query(
        DiscussionThread
    ).filter(
        DiscussionThread.id == thread_id
    ).first()

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found"
        )

    # -----------------------------------------------------
    # CREATE REPLY
    # -----------------------------------------------------

    new_reply = Comment(
        decision_id=thread.decision_id,
        thread_id=thread_id,
        user_id=current_user.id,
        content=comment.content
    )

    db.add(new_reply)

    db.flush()

    # -----------------------------------------------------
    # AUDIT - CREATE REPLY
    #
    # A reply is still a Comment entity.
    # -----------------------------------------------------

    log_audit(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Comment",
        entity_id=new_reply.id,
        description=(
            f"User {current_user.id} created "
            f"Comment {new_reply.id} as a reply "
            f"to DiscussionThread {thread_id}"
        ),
        new_value=comment_to_dict(new_reply),
        request_method="POST",
        endpoint=f"/threads/{thread_id}/comments"
    )

    # -----------------------------------------------------
    # COMMIT
    # -----------------------------------------------------

    db.commit()
    db.refresh(new_reply)

    return new_reply


# =========================================================
# GET ALL REPLIES FOR A DISCUSSION THREAD
# =========================================================

@router.get(
    "/threads/{thread_id}/comments",
    response_model=list[CommentResponse]
)
def get_thread_replies(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # -----------------------------------------------------
    # CHECK THREAD
    # -----------------------------------------------------

    thread = db.query(
        DiscussionThread
    ).filter(
        DiscussionThread.id == thread_id
    ).first()

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found"
        )

    # -----------------------------------------------------
    # GET REPLIES
    # -----------------------------------------------------

    replies = db.query(
        Comment
    ).filter(
        Comment.thread_id == thread_id
    ).all()

    return replies