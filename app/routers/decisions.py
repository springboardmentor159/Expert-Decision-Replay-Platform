from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.decision import Decision
from app.models.tag import Tag
from app.models.user import User
from app.schemas.decision import (
    DecisionCreate,
    DecisionRationaleResponse,
    DecisionRationaleUpdate,
    DecisionResponse,
    DecisionSearchItem,
    DecisionSearchResponse,
    DecisionStatus,
    DecisionStatusUpdate,
    DecisionTimelineResponse,
    DecisionUpdate,
    TimelineEvent,
)
from app.schemas.tag import DecisionTagAssign, TagResponse
from app.services.activity_logger import log_activity

router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)

ALLOWED_SORT_FIELDS = {
    "created_at": Decision.created_at,
    "updated_at": Decision.updated_at,
    "title": Decision.title,
}


@router.post(
    "",
    response_model=DecisionResponse,
    status_code=http_status.HTTP_201_CREATED,
    summary="Create a new decision"
)
def create_decision(
    decision: DecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_decision = Decision(
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status="Draft",
        created_by=current_user.id
    )
    db.add(new_decision)
    db.commit()
    db.refresh(new_decision)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="create",
        entity_type="Decision",
        entity_id=new_decision.id,
        description=f"User {current_user.full_name} created decision '{new_decision.title}'"
    )

    return new_decision


@router.get(
    "/search",
    response_model=DecisionSearchResponse,
    summary="Search decisions with keywords, category, status, and tag filters"
)
def search_decisions(
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[DecisionStatus] = Query(None),
    tag: Optional[str] = Query(None),
    sort: str = Query("created_at"),
    order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if sort not in ALLOWED_SORT_FIELDS:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid sort field '{sort}'. Allowed fields: {list(ALLOWED_SORT_FIELDS.keys())}"
        )

    if order.lower() not in ["asc", "desc"]:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid order. Allowed values: 'asc', 'desc'"
        )

    query = db.query(Decision)

    if q:
        search_pattern = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Decision.title.ilike(search_pattern),
                Decision.problem_statement.ilike(search_pattern),
                Decision.rationale.ilike(search_pattern)
            )
        )

    if category:
        query = query.filter(Decision.category.ilike(category.strip()))

    if status:
        query = query.filter(Decision.status == status.value)

    if tag:
        query = query.filter(Decision.tags.any(Tag.name.ilike(tag.strip())))

    total = query.count()

    # Apply sorting
    sort_column = ALLOWED_SORT_FIELDS[sort]
    if order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    decisions = query.offset((page - 1) * page_size).limit(page_size).all()

    # Format search results
    search_items = [
        DecisionSearchItem(
            id=d.id,
            title=d.title,
            category=d.category,
            status=d.status,
            tags=[t.name for t in d.tags],
            created_at=d.created_at,
            updated_at=d.updated_at
        )
        for d in decisions
    ]

    return DecisionSearchResponse(
        items=decisions,
        results=search_items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get(
    "",
    response_model=List[DecisionResponse],
    summary="Get all decisions with optional status, category, tag, and sort filters"
)
def get_decisions(
    status: Optional[DecisionStatus] = Query(None),
    category: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    order: Optional[str] = Query("desc"),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Decision)

    if status:
        query = query.filter(Decision.status == status.value)

    if category:
        query = query.filter(Decision.category.ilike(category.strip()))

    if tag:
        query = query.filter(Decision.tags.any(Tag.name.ilike(tag.strip())))

    if sort:
        if sort not in ALLOWED_SORT_FIELDS:
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid sort field '{sort}'. Allowed fields: {list(ALLOWED_SORT_FIELDS.keys())}"
            )
        if order and order.lower() not in ["asc", "desc"]:
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid order. Allowed values: 'asc', 'desc'"
            )
        sort_column = ALLOWED_SORT_FIELDS[sort]
        if order and order.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(Decision.created_at.desc())

    if page is not None and page_size is not None:
        query = query.offset((page - 1) * page_size).limit(page_size)

    return query.all()


@router.get(
    "/{decision_id}",
    response_model=DecisionResponse,
    summary="Get decision by ID"
)
def get_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )
    return decision


@router.put(
    "/{decision_id}",
    response_model=DecisionResponse,
    summary="Update decision details"
)
def update_decision(
    decision_id: int,
    decision_update: DecisionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    if decision.status == "Archived":
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify an archived decision"
        )

    decision.title = decision_update.title
    decision.problem_statement = decision_update.problem_statement
    decision.category = decision_update.category
    decision.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(decision)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="update",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"User {current_user.full_name} updated decision '{decision.title}'"
    )

    return decision


@router.patch(
    "/{decision_id}/status",
    response_model=DecisionResponse,
    summary="Update decision status"
)
def update_decision_status(
    decision_id: int,
    status_update: DecisionStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    old_status = decision.status
    new_status = status_update.status.value

    if old_status == "Archived" and new_status == "Archived":
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify an archived decision"
        )

    decision.status = new_status
    decision.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(decision)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="status_change",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"User {current_user.full_name} changed status of decision '{decision.title}' from '{old_status}' to '{new_status}'"
    )

    return decision


@router.put(
    "/{decision_id}/rationale",
    response_model=DecisionRationaleResponse,
    status_code=http_status.HTTP_200_OK,
    summary="Record decision rationale"
)
def update_decision_rationale(
    decision_id: int,
    rationale_update: DecisionRationaleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    if decision.status == "Archived":
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify an archived decision"
        )

    if decision.created_by != current_user.id and current_user.role not in ["Administrator", "Manager"]:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update decision rationale"
        )

    decision.rationale = rationale_update.rationale
    decision.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(decision)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="update_rationale",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"User {current_user.full_name} recorded rationale for decision '{decision.title}'"
    )

    return DecisionRationaleResponse(
        decision_id=decision.id,
        rationale=decision.rationale
    )


@router.get(
    "/{decision_id}/rationale",
    response_model=DecisionRationaleResponse,
    status_code=http_status.HTTP_200_OK,
    summary="Get decision rationale"
)
def get_decision_rationale(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return DecisionRationaleResponse(
        decision_id=decision.id,
        rationale=decision.rationale
    )


# =============================================================================
# TAG ASSOCIATIONS FOR DECISIONS
# =============================================================================

@router.post(
    "/{decision_id}/tags",
    response_model=DecisionResponse,
    status_code=http_status.HTTP_200_OK,
    summary="Assign tags to a decision"
)
def assign_tags_to_decision(
    decision_id: int,
    tag_data: DecisionTagAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    if decision.status == "Archived":
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify an archived decision"
        )

    # Validate that all tag IDs exist
    existing_tags = db.query(Tag).filter(Tag.id.in_(tag_data.tag_ids)).all()
    found_ids = {t.id for t in existing_tags}
    missing_ids = set(tag_data.tag_ids) - found_ids

    if missing_ids:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Tag IDs not found: {list(missing_ids)}"
        )

    # Add tags without duplicate associations
    current_tag_ids = {t.id for t in decision.tags}
    for tag_obj in existing_tags:
        if tag_obj.id not in current_tag_ids:
            decision.tags.append(tag_obj)

    db.commit()
    db.refresh(decision)

    tag_names = ", ".join([t.name for t in existing_tags])
    log_activity(
        db=db,
        user_id=current_user.id,
        action="assign_tags",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"User {current_user.full_name} assigned tags [{tag_names}] to Decision #{decision.id}"
    )

    return decision


@router.get(
    "/{decision_id}/tags",
    response_model=List[TagResponse],
    summary="Get tags assigned to a decision"
)
def get_decision_tags(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )
    return decision.tags


@router.delete(
    "/{decision_id}/tags/{tag_id}",
    status_code=http_status.HTTP_200_OK,
    summary="Remove a tag from a decision"
)
def remove_tag_from_decision(
    decision_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    if decision.status == "Archived":
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify an archived decision"
        )

    tag_to_remove = None
    for t in decision.tags:
        if t.id == tag_id:
            tag_to_remove = t
            break

    if not tag_to_remove:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} is not associated with this decision"
        )

    decision.tags.remove(tag_to_remove)
    db.commit()

    log_activity(
        db=db,
        user_id=current_user.id,
        action="remove_tag",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"User {current_user.full_name} removed tag '{tag_to_remove.name}' from Decision #{decision.id}"
    )

    return {"message": f"Tag '{tag_to_remove.name}' removed from decision successfully"}


# =============================================================================
# DECISION TIMELINE
# =============================================================================

@router.get(
    "/{decision_id}/timeline",
    response_model=DecisionTimelineResponse,
    summary="Get chronological timeline of events for a decision"
)
def get_decision_timeline(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    events: List[TimelineEvent] = []

    # 1. Decision Created
    events.append(
        TimelineEvent(
            event_type="Decision created",
            timestamp=decision.created_at,
            actor_id=decision.created_by,
            actor_name=decision.creator.full_name if decision.creator else None,
            details={"title": decision.title, "category": decision.category, "status": "Draft"}
        )
    )

    # 2. Decision Updated (if different timestamp)
    if decision.updated_at and decision.updated_at > decision.created_at:
        events.append(
            TimelineEvent(
                event_type="Decision updated",
                timestamp=decision.updated_at,
                actor_id=decision.created_by,
                actor_name=decision.creator.full_name if decision.creator else None,
                details={"status": decision.status}
            )
        )

    # 3. Alternatives Added
    for alt in decision.alternatives:
        events.append(
            TimelineEvent(
                event_type="Alternative added",
                timestamp=alt.created_at,
                details={"alternative_id": alt.id, "name": alt.name, "risk_level": alt.risk_level}
            )
        )

    # 4. Discussion Threads Started
    for thread in decision.threads:
        events.append(
            TimelineEvent(
                event_type="Discussion thread started",
                timestamp=thread.created_at,
                actor_id=thread.created_by,
                actor_name=thread.creator.full_name if thread.creator else None,
                details={"thread_id": thread.id, "title": thread.title}
            )
        )

    # 5. Comments Added
    for c in decision.comments:
        events.append(
            TimelineEvent(
                event_type="Comment added",
                timestamp=c.created_at,
                actor_id=c.user_id,
                actor_name=c.user.full_name if c.user else None,
                details={"comment_id": c.id, "content_snippet": c.content[:50]}
            )
        )

    # 6. Meeting Notes Recorded
    for note in decision.meeting_notes:
        events.append(
            TimelineEvent(
                event_type="Meeting note recorded",
                timestamp=note.created_at,
                actor_id=note.created_by,
                actor_name=note.creator.full_name if note.creator else None,
                details={"note_id": note.id, "title": note.title}
            )
        )

    # 7. Approvals
    for app in decision.approvals:
        events.append(
            TimelineEvent(
                event_type="Approval assigned",
                timestamp=app.created_at,
                actor_id=app.reviewer_id,
                actor_name=app.reviewer.full_name if app.reviewer else None,
                details={"approval_id": app.id, "status": "Pending"}
            )
        )
        if app.completed_at:
            event_type = "Decision approved" if app.status == "Approved" else "Decision rejected"
            events.append(
                TimelineEvent(
                    event_type=event_type,
                    timestamp=app.completed_at,
                    actor_id=app.reviewer_id,
                    actor_name=app.reviewer.full_name if app.reviewer else None,
                    details={"approval_id": app.id, "status": app.status, "comments": app.comments}
                )
            )

    # Sort events chronologically
    events.sort(key=lambda x: x.timestamp)

    return DecisionTimelineResponse(
        decision_id=decision.id,
        title=decision.title,
        current_status=decision.status,
        events=events
    )
