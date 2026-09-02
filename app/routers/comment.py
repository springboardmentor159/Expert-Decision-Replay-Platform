from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.discussion_thread import DiscussionThread
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from app.utils.security import get_current_user
from app.utils.activity_logger import log_activity
from app.utils.audit import log_audit


router = APIRouter(tags=["Comments"])


def get_decision_or_404(decision_id: int, db: Session) -> Decision:
    decision = db.query(Decision).filter(Decision.id == decision_id).first()

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return decision


def get_thread_or_404(thread_id: int, db: Session) -> DiscussionThread:
    thread = (
        db.query(DiscussionThread)
        .filter(DiscussionThread.id == thread_id)
        .first()
    )

    if thread is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found"
        )

    return thread


def get_comment_or_404(comment_id: int, db: Session) -> Comment:
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    return comment


def ensure_owner(comment: Comment, current_user: User) -> None:
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this comment"
        )


# CREATE COMMENT ON A DECISION
@router.post(
    "/decisions/{decision_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_comment(
    decision_id: int,
    comment: CommentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_decision_or_404(decision_id, db)

    new_comment = Comment(
        decision_id=decision_id,
        thread_id=None,
        user_id=current_user.id,
        content=comment.content
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    log_activity(
        db=db,
        user_id=current_user.id,
        action="comment_created",
        entity_type="Comment",
        entity_id=new_comment.id,
        description="A comment was added to a decision",
    )
    log_audit(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Comment",
        entity_id=new_comment.id,
        description=f"Comment added to decision {decision_id}",
        new_value={"decision_id": decision_id},
        request=request,
    )

    return new_comment


# GET ALL COMMENTS FOR A DECISION
@router.get(
    "/decisions/{decision_id}/comments",
    response_model=list[CommentResponse]
)
def get_comments(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_decision_or_404(decision_id, db)

    return (
        db.query(Comment)
        .filter(Comment.decision_id == decision_id)
        .order_by(Comment.created_at.asc())
        .all()
    )


# GET ONE COMMENT BY ID
@router.get(
    "/comments/{comment_id}",
    response_model=CommentResponse
)
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_comment_or_404(comment_id, db)


# UPDATE COMMENT
@router.put(
    "/comments/{comment_id}",
    response_model=CommentResponse
)
def update_comment(
    comment_id: int,
    data: CommentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = get_comment_or_404(comment_id, db)

    ensure_owner(comment, current_user)

    old_value = {"content": comment.content}

    # Only the content can ever be updated.
    # id, decision_id, thread_id, user_id, created_at are never touched.
    comment.content = data.content
    comment.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(comment)

    log_audit(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Comment",
        entity_id=comment.id,
        description=f"Comment {comment.id} was updated",
        old_value=old_value,
        new_value={"content": comment.content},
        request=request,
    )

    return comment


# DELETE COMMENT
@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = get_comment_or_404(comment_id, db)

    ensure_owner(comment, current_user)

    comment_id_snapshot = comment.id
    decision_id_snapshot = comment.decision_id

    db.delete(comment)
    db.commit()

    log_audit(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="Comment",
        entity_id=comment_id_snapshot,
        description=f"Comment {comment_id_snapshot} was deleted from decision {decision_id_snapshot}",
        request=request,
    )

    return {"message": "Comment deleted successfully"}


# CREATE REPLY INSIDE A DISCUSSION THREAD
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
    thread = get_thread_or_404(thread_id, db)

    new_comment = Comment(
        decision_id=thread.decision_id,
        thread_id=thread.id,
        user_id=current_user.id,
        content=comment.content
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment


# GET ALL REPLIES FOR A DISCUSSION THREAD
@router.get(
    "/threads/{thread_id}/comments",
    response_model=list[CommentResponse]
)
def get_thread_replies(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_thread_or_404(thread_id, db)

    return (
        db.query(Comment)
        .filter(Comment.thread_id == thread_id)
        .order_by(Comment.created_at.asc())
        .all()
    )
