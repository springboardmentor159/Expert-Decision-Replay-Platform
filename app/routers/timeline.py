from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db

from app.models.user import User
from app.models.decision import Decision
from app.models.alternative import Alternative
from app.models.discussion_thread import DiscussionThread
from app.models.comment import Comment

from app.schemas.timeline import TimelineEvent


router = APIRouter(
    prefix="/decisions",
    tags=["Timeline"]
)


@router.get(
    "/{decision_id}/timeline",
    response_model=List[TimelineEvent]
)
def get_decision_timeline(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Find decision
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    events = []

    # -------------------------
    # Decision Created
    # -------------------------
    events.append(
        TimelineEvent(
            event_type="Decision Created",
            description=f"Decision '{decision.title}' was created",
            timestamp=decision.created_at
        )
    )

    # -------------------------
    # Alternatives Created
    # -------------------------
    alternatives = (
        db.query(Alternative)
        .filter(
            Alternative.decision_id == decision_id
        )
        .all()
    )

    for alternative in alternatives:
        events.append(
            TimelineEvent(
                event_type="Alternative Created",
                description=f"Alternative '{alternative.name}' was added",
                timestamp=alternative.created_at
            )
        )

    # -------------------------
    # Discussion Threads Created
    # -------------------------
    discussion_threads = (
        db.query(DiscussionThread)
        .filter(
            DiscussionThread.decision_id == decision_id
        )
        .all()
    )

    for thread in discussion_threads:
        events.append(
            TimelineEvent(
                event_type="Discussion Thread Created",
                description=f"Discussion thread '{thread.title}' was created",
                timestamp=thread.created_at
            )
        )

    # -------------------------
    # Comments Added
    # -------------------------
    comments = (
        db.query(Comment)
        .filter(
            Comment.decision_id == decision_id
        )
        .all()
    )

    for comment in comments:
        events.append(
            TimelineEvent(
                event_type="Comment Added",
                description="A comment was added to the decision",
                timestamp=comment.created_at
            )
        )

    # -------------------------
    # Decision Updated
    # -------------------------
    if decision.updated_at != decision.created_at:
        events.append(
            TimelineEvent(
                event_type="Decision Updated",
                description=f"Decision '{decision.title}' was updated",
                timestamp=decision.updated_at
            )
        )

    # -------------------------
    # Sort Timeline
    # -------------------------
    events.sort(
        key=lambda event: event.timestamp
    )

    return events