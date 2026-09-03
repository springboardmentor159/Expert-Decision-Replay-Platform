from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.services.activity_service import log_activity
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.decision import Decision
from app.models.discussion_thread import DiscussionThread
from pydantic import BaseModel


router = APIRouter(
    prefix="/decisions",
    tags=["Discussion Threads"]
)


class DiscussionThreadCreate(BaseModel):
    title: str
    content: str


class DiscussionThreadResponse(BaseModel):
    id: int
    decision_id: int
    user_id: int
    title: str
    content: str

    class Config:
        from_attributes = True


@router.post(
    "/{decision_id}/discussion-threads",
    response_model=DiscussionThreadResponse,
    status_code=status.HTTP_201_CREATED
)
def create_thread(
    decision_id: int,
    thread_data: DiscussionThreadCreate,
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

    thread = DiscussionThread(
        decision_id=decision_id,
        user_id=current_user.id,
        title=thread_data.title,
        content=thread_data.content
    )

    db.add(thread)
    db.flush()

    log_activity(
        db=db,
        user_id=current_user.id,
        action="Discussion Thread Created",
        entity_type="DiscussionThread",
        entity_id=thread.id,
        description=(
            f"User {current_user.id} created Discussion Thread "
            f"{thread.id} for Decision {decision_id}"
        )
    )

    db.commit()
    db.refresh(thread)

    return thread

@router.get(
    "/{decision_id}/discussion-threads",
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
            status_code=404,
            detail="Decision not found"
        )

    return db.query(DiscussionThread).filter(
        DiscussionThread.decision_id == decision_id
    ).all()