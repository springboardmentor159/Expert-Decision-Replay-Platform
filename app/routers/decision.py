from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db

from app.models.user import User
from app.models.decision import Decision
from app.models.alternative import Alternative
from app.models.discussion_thread import DiscussionThread
from app.models.comment import Comment
from app.models.tag import Tag

from app.schemas.timeline import TimelineEvent
from app.schemas.tag import TagAssignment, TagResponse
from app.schemas.decision import DecisionListResponse, DecisionListItem
router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)
router.get(
    "/{decision_id}/timeline",
    response_model=List[TimelineEvent]
)
def get_decision_timeline(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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

    # Decision created
    events.append(
        TimelineEvent(
            event_type="Decision Created",
            description=f"Decision '{decision.title}' was created",
            timestamp=decision.created_at
        )
    )

    # Alternatives
    alternatives = (
        db.query(Alternative)
        .filter(Alternative.decision_id == decision_id)
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

    # Discussion threads
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

    # Comments
    comments = (
        db.query(Comment)
        .filter(Comment.decision_id == decision_id)
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

    # Decision updated
    if decision.updated_at != decision.created_at:
        events.append(
            TimelineEvent(
                event_type="Decision Updated",
                description=f"Decision '{decision.title}' was updated",
                timestamp=decision.updated_at
            )
        )

    # Sort chronologically
    events.sort(key=lambda event: event.timestamp)

    return events
@router.get(
    "/search",
    response_model=DecisionListResponse
)
def search_decisions(
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),

    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),

    sort: str = Query("created_at"),
    order: str = Query("desc"),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Decision)

    # Keyword search
    if q:
        search_term = f"%{q}%"

        query = query.filter(
            or_(
                Decision.title.ilike(search_term),
                Decision.problem_statement.ilike(search_term),
                Decision.rationale.ilike(search_term)
            )
        )

    # Category filter
    if category:
        query = query.filter(
            Decision.category == category
        )

    # Status filter
    if status:
        allowed_statuses = [
            "Draft",
            "Under Review",
            "Approved",
            "Rejected",
            "Archived"
        ]

        if status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid status"
            )

        query = query.filter(
            Decision.status == status
        )

    # Tag filter
    if tag:
        query = query.filter(
            Decision.tags.any(
                name=tag
            )
        )

    # Allowed sorting fields
    allowed_sort_fields = {
        "created_at": Decision.created_at,
        "updated_at": Decision.updated_at,
        "title": Decision.title,
    }

    if sort not in allowed_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid sort field"
        )

    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Order must be 'asc' or 'desc'"
        )

    sort_column = allowed_sort_fields[sort]

    if order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Total records
    total = query.count()

    # Pagination
    offset = (page - 1) * page_size

    decisions = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # Convert database objects to response objects
    items = [
        DecisionListItem.model_validate(decision)
        for decision in decisions
    ]

    return DecisionListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )
@router.post(
    "/{decision_id}/tags",
    response_model=List[TagResponse]
)
def assign_tags_to_decision(
    decision_id: int,
    tag_data: TagAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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

    tags = (
        db.query(Tag)
        .filter(Tag.id.in_(tag_data.tag_ids))
        .all()
    )

    found_tag_ids = {tag.id for tag in tags}
    requested_tag_ids = set(tag_data.tag_ids)

    missing_tag_ids = requested_tag_ids - found_tag_ids

    if missing_tag_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag(s) not found: {sorted(missing_tag_ids)}"
        )

    existing_tag_ids = {tag.id for tag in decision.tags}

    for tag in tags:
        if tag.id not in existing_tag_ids:
            decision.tags.append(tag)

    db.commit()
    db.refresh(decision)

    return decision.tags
from app.schemas.decision import (
    DecisionListResponse,
    DecisionListItem,
)
from app.schemas.tag import (
    TagAssignment,
    TagResponse,
)