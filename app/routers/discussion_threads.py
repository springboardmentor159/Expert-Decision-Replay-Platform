from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.decision import Decision
from app.models.discussion_thread import DiscussionThread
from app.models.user import User
from app.schemas.audit_log import AuditAction, AuditEntityType
from app.services.activity_service import log_activity
from app.services.audit_service import log_audit


router = APIRouter(
    prefix="/decisions",
    tags=["Discussion Threads"],
)


ALLOWED_ROLES = {
    "Employee",
    "Reviewer",
    "Manager",
    "Administrator",
}


class DiscussionThreadCreate(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)


class DiscussionThreadResponse(BaseModel):
    id: int
    decision_id: int
    user_id: int
    title: str
    content: str

    model_config = ConfigDict(from_attributes=True)


def get_decision_or_404(
    decision_id: int,
    db: Session,
) -> Decision:
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    return decision


def ensure_decision_access(
    decision: Decision,
    current_user: User,
) -> None:
    role = str(current_user.role)

    if role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this decision",
        )

    if role == "Employee" and decision.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this decision",
        )


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


def validate_thread_content(
    title: str,
    content: str,
) -> tuple[str, str]:
    cleaned_title = title.strip()
    cleaned_content = content.strip()

    if not cleaned_title:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Discussion thread title cannot be empty",
        )

    if not cleaned_content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Discussion thread content cannot be empty",
        )

    return cleaned_title, cleaned_content


# CREATE DISCUSSION THREAD
@router.post(
    "/{decision_id}/discussion-threads",
    response_model=DiscussionThreadResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_thread(
    decision_id: int,
    thread_data: DiscussionThreadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        decision_id=decision_id,
        db=db,
    )

    ensure_decision_access(
        decision=decision,
        current_user=current_user,
    )

    title, content = validate_thread_content(
        thread_data.title,
        thread_data.content,
    )

    thread = DiscussionThread(
        decision_id=decision_id,
        user_id=current_user.id,
        title=title,
        content=content,
    )

    db.add(thread)
    db.flush()

    description = (
        f"User {current_user.id} created Discussion Thread "
        f"{thread.id} for Decision {decision_id}"
    )

    log_audit(
        db=db,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type=AuditEntityType.DISCUSSION_THREAD,
        entity_id=thread.id,
        description=description,
        new_value={
            "decision_id": decision_id,
            "title": thread.title,
            "content": thread.content,
        },
        request_method="POST",
        endpoint=f"/decisions/{decision_id}/discussion-threads",
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="DiscussionThread",
        entity_id=thread.id,
        description=description,
    )

    db.commit()
    db.refresh(thread)

    return thread


# GET DISCUSSION THREADS
@router.get(
    "/{decision_id}/discussion-threads",
    response_model=list[DiscussionThreadResponse],
)
def get_threads(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        decision_id=decision_id,
        db=db,
    )

    ensure_decision_access(
        decision=decision,
        current_user=current_user,
    )

    return (
        db.query(DiscussionThread)
        .filter(
            DiscussionThread.decision_id == decision_id
        )
        .order_by(
            DiscussionThread.created_at.asc()
        )
        .all()
    )


# UPDATE DISCUSSION THREAD
@router.put(
    "/discussion-threads/{thread_id}",
    response_model=DiscussionThreadResponse,
)
def update_thread(
    thread_id: int,
    thread_data: DiscussionThreadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thread = get_thread_or_404(
        thread_id=thread_id,
        db=db,
    )

    decision = get_decision_or_404(
        decision_id=thread.decision_id,
        db=db,
    )

    ensure_decision_access(
        decision=decision,
        current_user=current_user,
    )

    if thread.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own discussion thread",
        )

    title, content = validate_thread_content(
        thread_data.title,
        thread_data.content,
    )

    old_title = thread.title
    old_content = thread.content

    thread.title = title
    thread.content = content

    description = (
        f"User {current_user.id} updated Discussion Thread "
        f"{thread.id}"
    )

    log_audit(
        db=db,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type=AuditEntityType.DISCUSSION_THREAD,
        entity_id=thread.id,
        description=description,
        old_value={
            "decision_id": thread.decision_id,
            "title": old_title,
            "content": old_content,
        },
        new_value={
            "decision_id": thread.decision_id,
            "title": thread.title,
            "content": thread.content,
        },
        request_method="PUT",
        endpoint=f"/decisions/discussion-threads/{thread.id}",
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="DiscussionThread",
        entity_id=thread.id,
        description=description,
    )

    db.commit()
    db.refresh(thread)

    return thread


# DELETE DISCUSSION THREAD
@router.delete(
    "/discussion-threads/{thread_id}",
    status_code=status.HTTP_200_OK,
)
def delete_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thread = get_thread_or_404(
        thread_id=thread_id,
        db=db,
    )

    decision = get_decision_or_404(
        decision_id=thread.decision_id,
        db=db,
    )

    ensure_decision_access(
        decision=decision,
        current_user=current_user,
    )

    if thread.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own discussion thread",
        )

    description = (
        f"User {current_user.id} deleted Discussion Thread "
        f"{thread.id}"
    )

    log_audit(
        db=db,
        user_id=current_user.id,
        action=AuditAction.DELETE,
        entity_type=AuditEntityType.DISCUSSION_THREAD,
        entity_id=thread.id,
        description=description,
        old_value={
            "decision_id": thread.decision_id,
            "title": thread.title,
            "content": thread.content,
        },
        request_method="DELETE",
        endpoint=f"/decisions/discussion-threads/{thread.id}",
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="DiscussionThread",
        entity_id=thread.id,
        description=description,
    )

    db.delete(thread)
    db.commit()

    return {
        "message": "Discussion thread deleted successfully",
    }