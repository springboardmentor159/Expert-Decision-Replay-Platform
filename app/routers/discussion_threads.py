from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.models.discussion_thread import DiscussionThread
from app.models.decision import Decision
from app.models.user import User

from app.schemas.discussion_thread import (
    DiscussionThreadCreate,
    DiscussionThreadUpdate,
    DiscussionThreadResponse
)

from app.core.security import get_current_user

from app.services.audit import log_audit


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    tags=["Discussion Threads"]
)


# =========================================================
# HELPER - THREAD TO DICTIONARY
# =========================================================

def thread_to_dict(thread: DiscussionThread):
    """
    Convert a discussion thread to a JSON-safe dictionary
    for audit history.
    """

    return {
        "id": thread.id,
        "decision_id": thread.decision_id,
        "created_by": thread.created_by,
        "title": thread.title,
        "description": thread.description,
        "status": thread.status
    }


# =========================================================
# CREATE THREAD
# =========================================================

@router.post(
    "/decisions/{decision_id}/threads",
    response_model=DiscussionThreadResponse,
    status_code=status.HTTP_201_CREATED
)
def create_thread(
    decision_id: int,
    thread_data: DiscussionThreadCreate,
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
    # CREATE THREAD
    # -----------------------------------------------------

    new_thread = DiscussionThread(
        decision_id=decision_id,
        created_by=current_user.id,
        title=thread_data.title,
        description=thread_data.description
    )

    db.add(new_thread)

    # Generate ID before audit.
    db.flush()

    # -----------------------------------------------------
    # AUDIT - CREATE THREAD
    # -----------------------------------------------------

    log_audit(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="DiscussionThread",
        entity_id=new_thread.id,
        description=(
            f"User {current_user.id} created "
            f"DiscussionThread {new_thread.id} "
            f"for Decision {decision_id}"
        ),
        new_value=thread_to_dict(new_thread),
        request_method="POST",
        endpoint=f"/decisions/{decision_id}/threads"
    )

    # -----------------------------------------------------
    # COMMIT
    # -----------------------------------------------------

    db.commit()
    db.refresh(new_thread)

    return new_thread


# =========================================================
# GET ALL THREADS FOR A DECISION
# =========================================================

@router.get(
    "/decisions/{decision_id}/threads",
    response_model=list[DiscussionThreadResponse]
)
def get_threads(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    threads = db.query(DiscussionThread).filter(
        DiscussionThread.decision_id == decision_id
    ).all()

    return threads


# =========================================================
# GET THREAD BY ID
# =========================================================

@router.get(
    "/threads/{thread_id}",
    response_model=DiscussionThreadResponse
)
def get_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    thread = db.query(DiscussionThread).filter(
        DiscussionThread.id == thread_id
    ).first()

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found"
        )

    return thread


# =========================================================
# UPDATE THREAD
# =========================================================

@router.put(
    "/threads/{thread_id}",
    response_model=DiscussionThreadResponse
)
def update_thread(
    thread_id: int,
    thread_data: DiscussionThreadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # -----------------------------------------------------
    # FIND THREAD
    # -----------------------------------------------------

    thread = db.query(DiscussionThread).filter(
        DiscussionThread.id == thread_id
    ).first()

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found"
        )

    # -----------------------------------------------------
    # AUTHORIZATION
    # -----------------------------------------------------

    if thread.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update this thread"
        )

    # -----------------------------------------------------
    # SAVE OLD VALUE
    # -----------------------------------------------------

    old_value = thread_to_dict(thread)

    # -----------------------------------------------------
    # UPDATE
    # -----------------------------------------------------

    update_data = thread_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    for field, value in update_data.items():
        setattr(
            thread,
            field,
            value
        )

    db.flush()

    # -----------------------------------------------------
    # SAVE NEW VALUE
    # -----------------------------------------------------

    new_value = thread_to_dict(thread)

    # -----------------------------------------------------
    # AUDIT - UPDATE THREAD
    # -----------------------------------------------------

    log_audit(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="DiscussionThread",
        entity_id=thread.id,
        description=(
            f"User {current_user.id} updated "
            f"DiscussionThread {thread.id}"
        ),
        old_value=old_value,
        new_value=new_value,
        request_method="PUT",
        endpoint=f"/threads/{thread_id}"
    )

    # -----------------------------------------------------
    # COMMIT
    # -----------------------------------------------------

    db.commit()
    db.refresh(thread)

    return thread


# =========================================================
# DELETE THREAD
# =========================================================

@router.delete(
    "/threads/{thread_id}"
)
def delete_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # -----------------------------------------------------
    # FIND THREAD
    # -----------------------------------------------------

    thread = db.query(DiscussionThread).filter(
        DiscussionThread.id == thread_id
    ).first()

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found"
        )

    # -----------------------------------------------------
    # AUTHORIZATION
    # -----------------------------------------------------

    if thread.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to delete this thread"
        )

    # -----------------------------------------------------
    # SAVE OLD VALUE
    # -----------------------------------------------------

    old_value = thread_to_dict(thread)

    decision_id = thread.decision_id

    # -----------------------------------------------------
    # AUDIT - DELETE THREAD
    # -----------------------------------------------------

    log_audit(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="DiscussionThread",
        entity_id=thread.id,
        description=(
            f"User {current_user.id} deleted "
            f"DiscussionThread {thread.id}"
        ),
        old_value=old_value,
        request_method="DELETE",
        endpoint=f"/threads/{thread_id}"
    )

    # -----------------------------------------------------
    # DELETE
    # -----------------------------------------------------

    db.delete(thread)

    db.commit()

    return {
        "message": "Discussion thread deleted successfully",
        "thread_id": thread_id,
        "decision_id": decision_id
    }