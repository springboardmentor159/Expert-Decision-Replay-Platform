from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.discussion_thread import DiscussionThread
from app.models.decision import Decision
from app.models.comment import Comment
from app.models.activity import Activity

from app.schemas.discussion_thread import (
    DiscussionThreadCreate,
    DiscussionThreadUpdate,
    DiscussionThreadResponse
)

from app.schemas.comment import (
    CommentCreate,
    CommentResponse
)

from app.core.security import get_current_user
from app.services.audit import create_audit_log


router = APIRouter(
    tags=["Discussion Threads"]
)


# ============================================================
# CREATE DISCUSSION THREAD
# POST /decisions/{decision_id}/threads
# ============================================================

@router.post(
    "/decisions/{decision_id}/threads",
    response_model=DiscussionThreadResponse,
    status_code=status.HTTP_201_CREATED
)
def create_thread(
    decision_id: int,
    thread_data: DiscussionThreadCreate,
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

    new_thread = DiscussionThread(
        decision_id=decision_id,
        created_by=current_user.id,
        title=thread_data.title,
        description=thread_data.description,
        status="Open"
    )

    db.add(new_thread)
    db.flush()

    # --------------------------------------------------------
    # ACTIVITY LOG
    # --------------------------------------------------------

    activity = Activity(
        user_id=current_user.id,
        action="Discussion Thread Created",
        entity_type="DiscussionThread",
        entity_id=new_thread.id,
        description=(
            f"User {current_user.id} created "
            f"Discussion Thread {new_thread.id} "
            f"for Decision {decision_id}"
        )
    )

    db.add(activity)

    # --------------------------------------------------------
    # AUDIT LOG
    # --------------------------------------------------------

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="DiscussionThread",
        entity_id=new_thread.id,
        description=(
            f"User {current_user.id} created "
            f"Discussion Thread {new_thread.id} "
            f"for Decision {decision_id}"
        ),
        new_value={
            "decision_id": decision_id,
            "title": thread_data.title,
            "description": thread_data.description,
            "status": "Open"
        }
    )

    db.commit()
    db.refresh(new_thread)

    return new_thread


# ============================================================
# GET ALL THREADS FOR DECISION
# GET /decisions/{decision_id}/threads
# ============================================================

@router.get(
    "/decisions/{decision_id}/threads",
    response_model=List[DiscussionThreadResponse]
)
def get_threads(
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
        db.query(DiscussionThread)
        .filter(
            DiscussionThread.decision_id == decision_id
        )
        .all()
    )


# ============================================================
# GET THREAD BY ID
# GET /threads/{thread_id}
# ============================================================

@router.get(
    "/threads/{thread_id}",
    response_model=DiscussionThreadResponse
)
def get_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    thread = (
        db.query(DiscussionThread)
        .filter(
            DiscussionThread.id == thread_id
        )
        .first()
    )

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found"
        )

    return thread


# ============================================================
# UPDATE OWN THREAD
# PUT /threads/{thread_id}
# ============================================================

@router.put(
    "/threads/{thread_id}",
    response_model=DiscussionThreadResponse
)
def update_thread(
    thread_id: int,
    thread_data: DiscussionThreadUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    thread = (
        db.query(DiscussionThread)
        .filter(
            DiscussionThread.id == thread_id
        )
        .first()
    )

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found"
        )

    if thread.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only update your own "
                "discussion threads"
            )
        )

    # --------------------------------------------------------
    # OLD VALUES
    # --------------------------------------------------------

    old_value = {
        "title": thread.title,
        "description": thread.description,
        "status": thread.status
    }

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    thread.title = thread_data.title
    thread.description = thread_data.description
    thread.status = thread_data.status

    new_value = {
        "title": thread.title,
        "description": thread.description,
        "status": thread.status
    }

    # --------------------------------------------------------
    # ACTIVITY LOG
    # --------------------------------------------------------

    activity = Activity(
        user_id=current_user.id,
        action="Discussion Thread Updated",
        entity_type="DiscussionThread",
        entity_id=thread.id,
        description=(
            f"User {current_user.id} updated "
            f"Discussion Thread {thread.id}"
        )
    )

    db.add(activity)

    # --------------------------------------------------------
    # AUDIT LOG
    # --------------------------------------------------------

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="DiscussionThread",
        entity_id=thread.id,
        description=(
            f"User {current_user.id} updated "
            f"Discussion Thread {thread.id}"
        ),
        old_value=old_value,
        new_value=new_value
    )

    db.commit()
    db.refresh(thread)

    return thread


# ============================================================
# DELETE OWN THREAD
# DELETE /threads/{thread_id}
# ============================================================

@router.delete(
    "/threads/{thread_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    thread = (
        db.query(DiscussionThread)
        .filter(
            DiscussionThread.id == thread_id
        )
        .first()
    )

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found"
        )

    if thread.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only delete your own "
                "discussion threads"
            )
        )

    # --------------------------------------------------------
    # SAVE OLD VALUE BEFORE DELETE
    # --------------------------------------------------------

    old_value = {
        "decision_id": thread.decision_id,
        "title": thread.title,
        "description": thread.description,
        "status": thread.status
    }

    thread_id_value = thread.id

    # --------------------------------------------------------
    # AUDIT LOG
    # --------------------------------------------------------

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="DiscussionThread",
        entity_id=thread_id_value,
        description=(
            f"User {current_user.id} deleted "
            f"Discussion Thread {thread_id_value}"
        ),
        old_value=old_value
    )

    # --------------------------------------------------------
    # ACTIVITY LOG
    # --------------------------------------------------------

    activity = Activity(
        user_id=current_user.id,
        action="Discussion Thread Deleted",
        entity_type="DiscussionThread",
        entity_id=thread_id_value,
        description=(
            f"User {current_user.id} deleted "
            f"Discussion Thread {thread_id_value}"
        )
    )

    db.add(activity)

    db.delete(thread)
    db.commit()

    return None


# ============================================================
# ADD REPLY TO THREAD
# POST /threads/{thread_id}/comments
# ============================================================

@router.post(
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
        .filter(
            DiscussionThread.id == thread_id
        )
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
    db.flush()

    # --------------------------------------------------------
    # AUDIT LOG
    # --------------------------------------------------------

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Comment",
        entity_id=new_reply.id,
        description=(
            f"User {current_user.id} created "
            f"Comment Reply {new_reply.id} "
            f"on Thread {thread_id}"
        ),
        new_value={
            "decision_id": thread.decision_id,
            "thread_id": thread_id,
            "content": comment.content
        }
    )

    # --------------------------------------------------------
    # ACTIVITY LOG
    # --------------------------------------------------------

    activity = Activity(
        user_id=current_user.id,
        action="Comment Reply Created",
        entity_type="Comment",
        entity_id=new_reply.id,
        description=(
            f"User {current_user.id} created "
            f"Comment Reply {new_reply.id} "
            f"on Thread {thread_id}"
        )
    )

    db.add(activity)

    db.commit()
    db.refresh(new_reply)

    return new_reply


# ============================================================
# GET THREAD REPLIES
# GET /threads/{thread_id}/comments
# ============================================================

@router.get(
    "/threads/{thread_id}/comments",
    response_model=List[CommentResponse]
)
def get_thread_replies(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    thread = (
        db.query(DiscussionThread)
        .filter(
            DiscussionThread.id == thread_id
        )
        .first()
    )

    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion thread not found"
        )

    return (
        db.query(Comment)
        .filter(
            Comment.thread_id == thread_id
        )
        .all()
    )