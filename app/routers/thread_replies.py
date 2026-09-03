from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.discussion_thread import DiscussionThread
from app.models.thread_reply import ThreadReply
from app.models.user import User


router = APIRouter(
    prefix="/discussion-threads",
    tags=["Thread Replies"]
)


class ThreadReplyCreate(BaseModel):
    content: str


class ThreadReplyResponse(BaseModel):
    id: int
    thread_id: int
    user_id: int
    content: str

    class Config:
        from_attributes = True


@router.post(
    "/{thread_id}/replies",
    response_model=ThreadReplyResponse,
    status_code=status.HTTP_201_CREATED
)
def create_reply(
    thread_id: int,
    reply_data: ThreadReplyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = db.query(DiscussionThread).filter(
        DiscussionThread.id == thread_id
    ).first()

    if not thread:
        raise HTTPException(
            status_code=404,
            detail="Discussion thread not found"
        )

    reply = ThreadReply(
        thread_id=thread_id,
        user_id=current_user.id,
        content=reply_data.content
    )

    db.add(reply)
    db.commit()
    db.refresh(reply)

    return reply


@router.get(
    "/{thread_id}/replies",
    response_model=list[ThreadReplyResponse]
)
def get_replies(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thread = db.query(DiscussionThread).filter(
        DiscussionThread.id == thread_id
    ).first()

    if not thread:
        raise HTTPException(
            status_code=404,
            detail="Discussion thread not found"
        )

    return db.query(ThreadReply).filter(
        ThreadReply.thread_id == thread_id
    ).all()