from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.models.discussion_thread import DiscussionThread
from app.schemas.discussion_thread import (
    DiscussionThreadCreate,
    DiscussionThreadUpdate,
    DiscussionThreadResponse,
)
from app.core.dependencies import get_current_user
from app.core.audit_logger import create_audit_log


router = APIRouter(
    tags=["Discussion Threads"]
)


# =========================================================
# CREATE DISCUSSION THREAD
# POST /decisions/{decision_id}/threads
# =========================================================

@router.post(
    "/decisions/{decision_id}/threads",
    response_model=DiscussionThreadResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_thread(
    decision_id: int,
    thread: DiscussionThreadCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Check whether decision exists
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

    # Create discussion thread
    db_thread = DiscussionThread(
        decision_id=decision_id,
        created_by=current_user.id,
        title=thread.title,
        description=thread.description,
        status="Open",
    )

    db.add(db_thread)
    db.commit()
    db.refresh(db_thread)

    # Audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="DiscussionThread",
        entity_id=db_thread.id,
        description="Created a discussion thread",
        new_value={
            "decision_id": decision_id,
            "created_by": current_user.id,
            "title": db_thread.title,
            "description": db_thread.description,
            "status": db_thread.status,
        },
        request_method="POST",
        endpoint=f"/decisions/{decision_id}/threads",
    )

    return db_thread


# =========================================================
# GET ALL THREADS FOR A DECISION
# GET /decisions/{decision_id}/threads
# =========================================================

@router.get(
    "/decisions/{decision_id}/threads",
    response_model=list[DiscussionThreadResponse],
)
def get_threads(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Check whether decision exists
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

    threads = (
        db.query(DiscussionThread)
        .filter(
            DiscussionThread.decision_id == decision_id
        )
        .order_by(DiscussionThread.created_at.asc())
        .all()
    )

    return threads


# =========================================================
# GET THREAD BY ID
# GET /threads/{thread_id}
# =========================================================

@router.get(
    "/threads/{thread_id}",
    response_model=DiscussionThreadResponse,
)
def get_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
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


# =========================================================
# UPDATE THREAD
# PUT /threads/{thread_id}
# =========================================================

@router.put(
    "/threads/{thread_id}",
    response_model=DiscussionThreadResponse,
)
def update_thread(
    thread_id: int,
    thread_data: DiscussionThreadUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
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

    # Only creator can update
    if thread.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own discussion thread",
        )

    # Store old values
    old_value = {
        "title": thread.title,
        "description": thread.description,
        "status": thread.status,
    }

    # Update thread
    thread.title = thread_data.title
    thread.description = thread_data.description
    thread.status = thread_data.status

    db.commit()
    db.refresh(thread)

    # Audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="DiscussionThread",
        entity_id=thread.id,
        description="Updated a discussion thread",
        old_value=old_value,
        new_value={
            "title": thread.title,
            "description": thread.description,
            "status": thread.status,
        },
        request_method="PUT",
        endpoint=f"/threads/{thread_id}",
    )

    return thread


# =========================================================
# DELETE THREAD
# DELETE /threads/{thread_id}
# =========================================================

@router.delete(
    "/threads/{thread_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
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

    # Only creator can delete
    if thread.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own discussion thread",
        )

    # Store old values before deletion
    old_value = {
        "decision_id": thread.decision_id,
        "created_by": thread.created_by,
        "title": thread.title,
        "description": thread.description,
        "status": thread.status,
    }

    db.delete(thread)
    db.commit()

    # Audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="DiscussionThread",
        entity_id=thread_id,
        description="Deleted a discussion thread",
        old_value=old_value,
        request_method="DELETE",
        endpoint=f"/threads/{thread_id}",
    )

    return None