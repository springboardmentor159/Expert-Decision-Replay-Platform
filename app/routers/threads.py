from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.decision import Decision
from app.models.discussion_thread import DiscussionThread
from app.models.comment import Comment
from app.schemas.discussion_thread import (
    ThreadCreate,
    ThreadUpdate,
    ThreadResponse
)
from app.schemas.comment import CommentCreate, CommentResponse


router = APIRouter(
    tags=["Discussion Threads"]
)


@router.post(
    "/decisions/{decision_id}/threads",
    response_model=ThreadResponse,
    status_code=status.HTTP_201_CREATED
)
def create_thread(
    decision_id: int,
    thread_data: ThreadCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    thread = DiscussionThread(
        decision_id=decision_id,
        created_by=int(current_user["sub"]),
        title=thread_data.title,
        description=thread_data.description
    )

    db.add(thread)
    db.commit()
    db.refresh(thread)

    return thread


@router.get(
    "/decisions/{decision_id}/threads",
    response_model=list[ThreadResponse]
)
def get_threads(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    return db.query(DiscussionThread).filter(
        DiscussionThread.decision_id == decision_id
    ).all()


@router.get(
    "/threads/{thread_id}",
    response_model=ThreadResponse
)
def get_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    thread = db.query(DiscussionThread).filter(
        DiscussionThread.id == thread_id
    ).first()

    if thread is None:
        raise HTTPException(
            status_code=404,
            detail="Thread not found"
        )

    return thread


@router.put(
    "/threads/{thread_id}",
    response_model=ThreadResponse
)
def update_thread(
    thread_id: int,
    thread_data: ThreadUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    thread = db.query(DiscussionThread).filter(
        DiscussionThread.id == thread_id
    ).first()

    if thread is None:
        raise HTTPException(
            status_code=404,
            detail="Thread not found"
        )

    if thread.created_by != int(current_user["sub"]):
        raise HTTPException(
            status_code=403,
            detail="You can only update your own thread"
        )

    thread.title = thread_data.title
    thread.description = thread_data.description
    thread.status = thread_data.status

    db.commit()
    db.refresh(thread)

    return thread


@router.delete("/threads/{thread_id}")
def delete_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    thread = db.query(DiscussionThread).filter(
        DiscussionThread.id == thread_id
    ).first()

    if thread is None:
        raise HTTPException(
            status_code=404,
            detail="Thread not found"
        )

    if thread.created_by != int(current_user["sub"]):
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own thread"
        )

    db.delete(thread)
    db.commit()

    return {
        "message": "Thread deleted successfully"
    }


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
    thread = db.query(DiscussionThread).filter(
        DiscussionThread.id == thread_id
    ).first()

    if thread is None:
        raise HTTPException(
            status_code=404,
            detail="Thread not found"
        )

    comment = Comment(
        decision_id=thread.decision_id,
        thread_id=thread_id,
        user_id=int(current_user["sub"]),
        content=comment_data.content
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment