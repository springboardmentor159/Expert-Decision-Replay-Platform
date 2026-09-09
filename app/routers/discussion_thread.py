from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.models.decision import Decision
from app.models.discussion_thread import DiscussionThread
from app.models.user import User

from app.schemas.discussion_thread import (
    DiscussionThreadCreate,
    DiscussionThreadUpdate,
    DiscussionThreadResponse,
)

from app.core.security import get_current_user

from app.services.activity_log import create_activity_log
from app.services.audit_log import create_audit_log
from app.services.access_log import create_access_log

from app.models.audit_action import AuditAction
from app.models.audit_entity import AuditEntityType


router = APIRouter(tags=["Discussion Threads"])


def get_decision_or_404(
    decision_id: int,
    db: Session
) -> Decision:
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return decision


def get_thread_or_404(
    thread_id: int,
    db: Session
) -> DiscussionThread:
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


def ensure_owner(
    thread: DiscussionThread,
    current_user: User
) -> None:
    if thread.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this thread"
        )


# ==========================================
# CREATE DISCUSSION THREAD
# ==========================================
@router.post(
    "/decisions/{decision_id}/threads",
    response_model=DiscussionThreadResponse,
    status_code=status.HTTP_201_CREATED
)
def create_thread(
    decision_id: int,
    thread: DiscussionThreadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = get_decision_or_404(decision_id, db)

    new_thread = DiscussionThread(
        decision_id=decision_id,
        created_by=current_user.id,
        title=thread.title,
        description=thread.description,
        status="Open"
    )

    db.add(new_thread)
    db.flush()

    # ==========================================
    # ACTIVITY LOG
    # ==========================================

    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="created",
        entity_type="discussion_thread",
        entity_id=new_thread.id,
        description=f"Created discussion thread: {new_thread.title}",
    )

    # ==========================================
    # AUDIT LOG
    # ==========================================

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type=AuditEntityType.DISCUSSION_THREAD,
        entity_id=new_thread.id,
        description=f"Created discussion thread: {new_thread.title}",
        new_value={
            "decision_id": decision_id,
            "title": new_thread.title,
            "description": new_thread.description,
            "status": new_thread.status,
            "created_by": current_user.id
        },
        request_method="POST",
        endpoint=f"/decisions/{decision_id}/threads"
    )

    db.commit()
    db.refresh(new_thread)

    return new_thread


# ==========================================
# GET ALL THREADS FOR A DECISION
# ==========================================
@router.get(
    "/decisions/{decision_id}/threads",
    response_model=list[DiscussionThreadResponse]
)
def get_threads(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_decision_or_404(decision_id, db)

    threads = (
        db.query(DiscussionThread)
        .filter(DiscussionThread.decision_id == decision_id)
        .all()
    )

    # ==========================================
    # ACCESS LOG
    # ==========================================

    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="DiscussionThread",
        resource_id=decision_id,
        action="LIST"
    )

    db.commit()

    return threads


# ==========================================
# GET THREAD BY ID
# ==========================================
@router.get(
    "/threads/{thread_id}",
    response_model=DiscussionThreadResponse
)
def get_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = get_thread_or_404(thread_id, db)

    # ==========================================
    # ACCESS LOG
    # ==========================================

    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="DiscussionThread",
        resource_id=thread.id,
        action="VIEW"
    )

    db.commit()

    return thread


# ==========================================
# UPDATE THREAD
# ==========================================
@router.put(
    "/threads/{thread_id}",
    response_model=DiscussionThreadResponse
)
def update_thread(
    thread_id: int,
    data: DiscussionThreadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = get_thread_or_404(thread_id, db)

    ensure_owner(thread, current_user)

    # ==========================================
    # SAVE OLD VALUES FOR AUDIT
    # ==========================================

    old_value = {
        "title": thread.title,
        "description": thread.description,
        "status": thread.status
    }

    if data.title is not None:
        thread.title = data.title

    if data.description is not None:
        thread.description = data.description

    if data.status is not None:
        thread.status = data.status.value

    thread.updated_at = datetime.utcnow()

    # ==========================================
    # ACTIVITY LOG
    # ==========================================

    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="updated",
        entity_type="discussion_thread",
        entity_id=thread.id,
        description=f"Updated discussion thread: {thread.title}",
    )

    # ==========================================
    # AUDIT LOG
    # ==========================================

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type=AuditEntityType.DISCUSSION_THREAD,
        entity_id=thread.id,
        description=f"Updated discussion thread: {thread.title}",
        old_value=old_value,
        new_value={
            "title": thread.title,
            "description": thread.description,
            "status": thread.status
        },
        request_method="PUT",
        endpoint=f"/threads/{thread_id}"
    )

    # ==========================================
    # ACCESS LOG
    # ==========================================

    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="DiscussionThread",
        resource_id=thread.id,
        action="UPDATE"
    )

    db.commit()
    db.refresh(thread)

    return thread


# ==========================================
# DELETE THREAD
# ==========================================
@router.delete(
    "/threads/{thread_id}"
)
def delete_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = get_thread_or_404(thread_id, db)

    ensure_owner(thread, current_user)

    # ==========================================
    # SAVE VALUES BEFORE DELETE
    # ==========================================

    old_value = {
        "decision_id": thread.decision_id,
        "title": thread.title,
        "description": thread.description,
        "status": thread.status,
        "created_by": thread.created_by
    }

    # ==========================================
    # ACTIVITY LOG
    # ==========================================

    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="deleted",
        entity_type="discussion_thread",
        entity_id=thread.id,
        description=f"Deleted discussion thread: {thread.title}",
    )

    # ==========================================
    # AUDIT LOG
    # ==========================================

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.DELETE,
        entity_type=AuditEntityType.DISCUSSION_THREAD,
        entity_id=thread.id,
        description=f"Deleted discussion thread: {thread.title}",
        old_value=old_value,
        request_method="DELETE",
        endpoint=f"/threads/{thread_id}"
    )

    # ==========================================
    # ACCESS LOG
    # ==========================================

    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="DiscussionThread",
        resource_id=thread.id,
        action="DELETE"
    )

    db.delete(thread)
    db.commit()

    return {
        "message": "Discussion thread deleted successfully"
    }