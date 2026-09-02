from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
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
from app.utils.security import get_current_user
from app.utils.activity_logger import log_activity
from app.utils.audit import log_audit


router = APIRouter(tags=["Discussion Threads"])


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


def ensure_owner(thread: DiscussionThread, current_user: User) -> None:
    if thread.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this thread"
        )


# CREATE DISCUSSION THREAD
@router.post(
    "/decisions/{decision_id}/threads",
    response_model=DiscussionThreadResponse,
    status_code=status.HTTP_201_CREATED
)
def create_thread(
    decision_id: int,
    thread: DiscussionThreadCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_decision_or_404(decision_id, db)

    new_thread = DiscussionThread(
        decision_id=decision_id,
        created_by=current_user.id,
        title=thread.title,
        description=thread.description,
        status="Open"
    )

    db.add(new_thread)
    db.commit()
    db.refresh(new_thread)
    log_activity(
        db=db,
        user_id=current_user.id,
        action="discussion_thread_created",
        entity_type="DiscussionThread",
        entity_id=new_thread.id,
        description=f"Discussion thread '{new_thread.title}' was started",
    )
    log_audit(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="DiscussionThread",
        entity_id=new_thread.id,
        description=f"Discussion thread '{new_thread.title}' was started on decision {decision_id}",
        new_value={"decision_id": decision_id, "title": new_thread.title},
        request=request,
    )

    return new_thread


# GET ALL THREADS FOR A DECISION
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

    return (
        db.query(DiscussionThread)
        .filter(DiscussionThread.decision_id == decision_id)
        .all()
    )


# GET THREAD BY ID
@router.get(
    "/threads/{thread_id}",
    response_model=DiscussionThreadResponse
)
def get_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_thread_or_404(thread_id, db)


# UPDATE THREAD
@router.put(
    "/threads/{thread_id}",
    response_model=DiscussionThreadResponse
)
def update_thread(
    thread_id: int,
    data: DiscussionThreadUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = get_thread_or_404(thread_id, db)

    ensure_owner(thread, current_user)

    old_value = {"title": thread.title, "status": thread.status}

    # Only these fields can ever be updated.
    # id, decision_id, created_by, created_at are never touched.
    if data.title is not None:
        thread.title = data.title

    if data.description is not None:
        thread.description = data.description

    if data.status is not None:
        thread.status = data.status.value

    thread.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(thread)

    log_audit(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="DiscussionThread",
        entity_id=thread.id,
        description=f"Discussion thread '{thread.title}' was updated",
        old_value=old_value,
        new_value={"title": thread.title, "status": thread.status},
        request=request,
    )

    return thread


# DELETE THREAD
@router.delete("/threads/{thread_id}")
def delete_thread(
    thread_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = get_thread_or_404(thread_id, db)

    ensure_owner(thread, current_user)

    thread_id_snapshot = thread.id
    decision_id_snapshot = thread.decision_id
    title_snapshot = thread.title

    db.delete(thread)
    db.commit()

    log_audit(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="DiscussionThread",
        entity_id=thread_id_snapshot,
        description=f"Discussion thread '{title_snapshot}' was deleted from decision {decision_id_snapshot}",
        request=request,
    )

    return {"message": "Discussion thread deleted successfully"}
