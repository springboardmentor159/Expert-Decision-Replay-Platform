from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.decision import Decision
from app.models.discussion_thread import DiscussionThread
from app.models.thread_reply import ThreadReply
from app.models.user import User
from app.schemas.audit_log import AuditAction, AuditEntityType
from app.services.activity_service import log_activity
from app.services.audit_service import log_audit


router = APIRouter(
    prefix="/discussion-threads",
    tags=["Thread Replies"],
)


ALLOWED_ROLES = {
    "Employee",
    "Reviewer",
    "Manager",
    "Administrator",
}


class ThreadReplyCreate(BaseModel):
    content: str = Field(min_length=1)


class ThreadReplyResponse(BaseModel):
    id: int
    thread_id: int
    user_id: int
    content: str

    model_config = ConfigDict(from_attributes=True)


def get_thread_or_404(
    thread_id: int,
    db: Session,
) -> DiscussionThread:
    thread = (
        db.query(DiscussionThread)
        .filter(DiscussionThread.id == thread_id)
        .first()
    )

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found",
        )

    return thread


def get_reply_or_404(
    reply_id: int,
    db: Session,
) -> ThreadReply:
    reply = (
        db.query(ThreadReply)
        .filter(ThreadReply.id == reply_id)
        .first()
    )

    if not reply:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread reply not found",
        )

    return reply


def get_decision_for_thread(
    thread: DiscussionThread,
    db: Session,
) -> Decision:
    decision = (
        db.query(Decision)
        .filter(Decision.id == thread.decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    return decision


def ensure_thread_access(
    thread: DiscussionThread,
    decision: Decision,
    current_user: User,
) -> None:
    role = str(current_user.role)

    if role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this discussion",
        )

    # Employees can access discussion threads only
    # for decisions they created.
    if role == "Employee" and decision.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this discussion",
        )


def validate_reply_content(content: str) -> str:
    if not isinstance(content, str):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Reply content must be a string",
        )

    cleaned_content = content.strip()

    if not cleaned_content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Reply content cannot be empty",
        )

    return cleaned_content


# CREATE REPLY
@router.post(
    "/{thread_id}/replies",
    response_model=ThreadReplyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_reply(
    thread_id: int,
    reply_data: ThreadReplyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thread = get_thread_or_404(
        thread_id=thread_id,
        db=db,
    )

    decision = get_decision_for_thread(
        thread=thread,
        db=db,
    )

    ensure_thread_access(
        thread=thread,
        decision=decision,
        current_user=current_user,
    )

    content = validate_reply_content(
        reply_data.content
    )

    reply = ThreadReply(
        thread_id=thread_id,
        user_id=current_user.id,
        content=content,
    )

    db.add(reply)
    db.flush()

    description = (
        f"User {current_user.id} created Thread Reply "
        f"{reply.id} for Discussion Thread {thread_id}"
    )

    log_audit(
        db=db,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type=AuditEntityType.COMMENT,
        entity_id=reply.id,
        description=description,
        new_value={
            "thread_id": thread_id,
            "content": reply.content,
        },
        request_method="POST",
        endpoint=f"/discussion-threads/{thread_id}/replies",
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="ThreadReply",
        entity_id=reply.id,
        description=description,
    )

    db.commit()
    db.refresh(reply)

    return reply


# GET REPLIES
@router.get(
    "/{thread_id}/replies",
    response_model=list[ThreadReplyResponse],
)
def get_replies(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thread = get_thread_or_404(
        thread_id=thread_id,
        db=db,
    )

    decision = get_decision_for_thread(
        thread=thread,
        db=db,
    )

    ensure_thread_access(
        thread=thread,
        decision=decision,
        current_user=current_user,
    )

    return (
        db.query(ThreadReply)
        .filter(ThreadReply.thread_id == thread_id)
        .order_by(ThreadReply.created_at.asc())
        .all()
    )


# UPDATE REPLY
@router.put(
    "/replies/{reply_id}",
    response_model=ThreadReplyResponse,
)
def update_reply(
    reply_id: int,
    reply_data: ThreadReplyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reply = get_reply_or_404(
        reply_id=reply_id,
        db=db,
    )

    thread = get_thread_or_404(
        thread_id=reply.thread_id,
        db=db,
    )

    decision = get_decision_for_thread(
        thread=thread,
        db=db,
    )

    ensure_thread_access(
        thread=thread,
        decision=decision,
        current_user=current_user,
    )

    if reply.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own reply",
        )

    content = validate_reply_content(
        reply_data.content
    )

    old_content = reply.content
    reply.content = content

    description = (
        f"User {current_user.id} updated Thread Reply "
        f"{reply.id}"
    )

    log_audit(
        db=db,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type=AuditEntityType.COMMENT,
        entity_id=reply.id,
        description=description,
        old_value={
            "thread_id": reply.thread_id,
            "content": old_content,
        },
        new_value={
            "thread_id": reply.thread_id,
            "content": reply.content,
        },
        request_method="PUT",
        endpoint=f"/discussion-threads/replies/{reply.id}",
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="ThreadReply",
        entity_id=reply.id,
        description=description,
    )

    db.commit()
    db.refresh(reply)

    return reply


# DELETE REPLY
@router.delete(
    "/replies/{reply_id}",
    status_code=status.HTTP_200_OK,
)
def delete_reply(
    reply_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reply = get_reply_or_404(
        reply_id=reply_id,
        db=db,
    )

    thread = get_thread_or_404(
        thread_id=reply.thread_id,
        db=db,
    )

    decision = get_decision_for_thread(
        thread=thread,
        db=db,
    )

    ensure_thread_access(
        thread=thread,
        decision=decision,
        current_user=current_user,
    )

    if reply.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reply",
        )

    old_content = reply.content

    description = (
        f"User {current_user.id} deleted Thread Reply "
        f"{reply.id}"
    )

    log_audit(
        db=db,
        user_id=current_user.id,
        action=AuditAction.DELETE,
        entity_type=AuditEntityType.COMMENT,
        entity_id=reply.id,
        description=description,
        old_value={
            "thread_id": reply.thread_id,
            "content": old_content,
        },
        request_method="DELETE",
        endpoint=f"/discussion-threads/replies/{reply.id}",
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="ThreadReply",
        entity_id=reply.id,
        description=description,
    )

    db.delete(reply)
    db.commit()

    return {
        "message": "Thread reply deleted successfully",
    }