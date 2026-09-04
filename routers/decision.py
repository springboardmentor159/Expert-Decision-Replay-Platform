from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc, func, or_
from sqlalchemy.orm import Session, selectinload

from app.core.auth import get_current_user
from app.db.database import get_db
from app.models.decision import Decision
from app.models.user import User
from app.models.alternative import Alternative
from app.models.activity import ActivityLog
from app.models.comment import Comment
from app.models.discussion_thread import DiscussionThread
from app.models.meeting_note import MeetingNote
from app.models.audit import AccessLog
from app.models.tag import Tag
from app.schemas.decision import (
    DecisionCreate,
    DecisionRationaleUpdate,
    DecisionResponse,
    DecisionStatus,
    DecisionCategory,
    DecisionStatusUpdate,
    DecisionUpdate,
    DecisionDiscoveryResponse,
    DecisionSearchResponse,
)
from app.schemas.tag import DecisionTagAssignment, TagResponse
from app.services.activity import record_activity
from app.services.audit import record_audit, record_decision_version

router = APIRouter(prefix="/decisions", tags=["Decisions"])


def _ensure_not_archived(decision: Decision) -> None:
    if decision.status == DecisionStatus.Archived.value:
        raise HTTPException(status_code=409, detail="Archived decisions cannot be modified")


def _ensure_can_modify(decision: Decision, user: User) -> None:
    if decision.created_by != user.id and str(user.role).lower() not in {"manager", "admin", "administrator"}:
        raise HTTPException(status_code=403, detail="Insufficient permission")


VALID_STATUS_TRANSITIONS = {
    DecisionStatus.Draft.value: {DecisionStatus.Draft.value, DecisionStatus.UnderReview.value, DecisionStatus.Archived.value},
    DecisionStatus.UnderReview.value: {DecisionStatus.UnderReview.value, DecisionStatus.Approved.value, DecisionStatus.Rejected.value},
    DecisionStatus.Approved.value: {DecisionStatus.Approved.value, DecisionStatus.Archived.value},
    DecisionStatus.Rejected.value: {DecisionStatus.Rejected.value, DecisionStatus.Draft.value, DecisionStatus.Archived.value},
    DecisionStatus.Archived.value: {DecisionStatus.Archived.value},
}


@router.post(
    "",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new decision",
    description="Create a new decision. User must be authenticated.",
)
def create_decision(
    decision: DecisionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new decision.
    - **title**: Decision title
    - **problem_statement**: Description of the problem
    - **category**: Decision category
    - Status is automatically set to "Draft"
    """
    db_decision = Decision(
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status=DecisionStatus.Draft.value,
        created_by=current_user.id,
    )
    db.add(db_decision)
    db.flush()
    record_activity(db, current_user.id, "decision_created", "Decision", "Decision created", db_decision.id)
    record_audit(db, current_user.id, "CREATE", "Decision", "Decision created", db_decision.id)
    record_decision_version(db, db_decision, current_user.id)
    db.commit()
    db.refresh(db_decision)
    return db_decision


@router.get(
    "",
    response_model=List[DecisionResponse] | DecisionDiscoveryResponse,
    summary="Get all decisions with optional filtering",
    description="Retrieve decisions. Can filter by status and/or category.",
)
def get_decisions(
    status: Optional[DecisionStatus] = Query(None, description="Filter by decision status"),
    category: Optional[DecisionCategory] = Query(None, description="Filter by decision category"),
    tag: Optional[str] = Query(None, description="Filter by tag name"),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=100),
    sort: str = Query("created_at", pattern="^(created_at|updated_at|title)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all decisions with optional filtering.
    - **status**: Filter by status (Draft, Under Review, Approved, Rejected, Archived)
    - **category**: Filter by category
    - User must be authenticated
    """
    query = db.query(Decision).options(selectinload(Decision.tags))

    if status:
        query = query.filter(Decision.status == status.value)

    if category:
        query = query.filter(Decision.category == category.value)

    if tag:
        query = query.join(Decision.tags).filter(func.lower(Tag.name) == tag.lower())

    sort_column = {"created_at": Decision.created_at, "updated_at": Decision.updated_at, "title": Decision.title}[sort]
    query = query.order_by((asc if order == "asc" else desc)(sort_column))
    if page is None and page_size is None:
        return query.all()
    page = page or 1
    page_size = page_size or 20
    total = query.order_by(None).count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.get("/search", response_model=DecisionSearchResponse)
def search_decisions(
    q: str = Query(min_length=1),
    status: Optional[DecisionStatus] = Query(None),
    category: Optional[DecisionCategory] = Query(None),
    tag: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort: str = Query("created_at", pattern="^(created_at|updated_at|title)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    term = f"%{q.lower()}%"
    query = db.query(Decision).options(selectinload(Decision.tags)).filter(
        or_(func.lower(Decision.title).like(term),
            func.lower(Decision.problem_statement).like(term),
            func.lower(func.coalesce(Decision.rationale, "")).like(term))
    )
    if status:
        query = query.filter(Decision.status == status.value)
    if category:
        query = query.filter(Decision.category == category.value)
    if tag:
        query = query.join(Decision.tags).filter(func.lower(Tag.name) == tag.lower())
    sort_column = {"created_at": Decision.created_at, "updated_at": Decision.updated_at, "title": Decision.title}[sort]
    query = query.order_by((asc if order == "asc" else desc)(sort_column))
    total = query.order_by(None).count()
    results = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"results": results, "items": results, "page": page, "page_size": page_size, "total": total}


@router.post("/{decision_id}/tags", response_model=list[TagResponse])
def assign_decision_tags(decision_id: int, payload: DecisionTagAssignment, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    _ensure_not_archived(decision)
    tags = db.query(Tag).filter(Tag.id.in_(set(payload.tag_ids))).all() if payload.tag_ids else []
    if len(tags) != len(set(payload.tag_ids)):
        raise HTTPException(status_code=404, detail="One or more tags not found")
    decision.tags = list({*decision.tags, *tags})
    db.commit()
    db.refresh(decision)
    return decision.tags


@router.get("/{decision_id}/tags", response_model=list[TagResponse])
def get_decision_tags(decision_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decision.tags


@router.delete("/{decision_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_decision_tag(decision_id: int, tag_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    _ensure_not_archived(decision)
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag or tag not in decision.tags:
        raise HTTPException(status_code=404, detail="Tag association not found")
    decision.tags.remove(tag)
    db.commit()


@router.get("/{decision_id}/timeline")
def get_decision_timeline(decision_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    events = [{"event_type": "Decision created", "timestamp": decision.created_at}]
    activities = db.query(ActivityLog).filter(
        ActivityLog.entity_type == "Decision", ActivityLog.entity_id == decision_id
    ).all()
    events += [
        {"event_type": item.action, "timestamp": item.created_at, "description": item.description}
        for item in activities if item.action != "decision_created"
    ]
    events += [{"event_type": "Alternative created", "timestamp": item.created_at} for item in db.query(Alternative).filter(Alternative.decision_id == decision_id)]
    events += [{"event_type": "Discussion thread created", "timestamp": item.created_at} for item in db.query(DiscussionThread).filter(DiscussionThread.decision_id == decision_id)]
    events += [{"event_type": "Comment added", "timestamp": item.created_at} for item in db.query(Comment).filter(Comment.decision_id == decision_id)]
    events += [{"event_type": "Meeting note created", "timestamp": item.created_at} for item in db.query(MeetingNote).filter(MeetingNote.decision_id == decision_id)]
    events.sort(key=lambda item: item["timestamp"])
    return events


@router.get(
    "/{decision_id}",
    response_model=DecisionResponse,
    summary="Get a specific decision",
    description="Retrieve a specific decision by ID.",
)
def get_decision(
    decision_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific decision by ID.
    - Returns 404 if decision not found
    """
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )
    db.add(AccessLog(user_id=current_user.id, resource_type="Decision", resource_id=decision.id, action="VIEW"))
    record_audit(db, current_user.id, "ACCESS", "Decision", "Decision viewed", decision.id)
    db.commit()
    return decision


@router.put(
    "/{decision_id}",
    response_model=DecisionResponse,
    summary="Update a decision",
    description="Update an existing decision. Fields like id, created_by, and created_at cannot be changed.",
)
def update_decision(
    decision_id: int,
    decision_update: DecisionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a decision.
    - **title**: Update the decision title (optional)
    - **problem_statement**: Update the problem statement (optional)
    - **category**: Update the category (optional)
    - Fields that CANNOT be changed: id, created_by, created_at
    - Returns 404 if decision not found
    """
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )
    _ensure_can_modify(decision, current_user)
    _ensure_not_archived(decision)
    old_value = {"title": decision.title, "problem_statement": decision.problem_statement, "category": decision.category}

    # Update only the allowed fields
    if decision_update.title is not None:
        decision.title = decision_update.title
    if decision_update.problem_statement is not None:
        decision.problem_statement = decision_update.problem_statement
    if decision_update.category is not None:
        decision.category = decision_update.category

    record_activity(db, current_user.id, "decision_updated", "Decision", "Decision updated", decision.id)
    new_value = {"title": decision.title, "problem_statement": decision.problem_statement, "category": decision.category}
    record_audit(db, current_user.id, "UPDATE", "Decision", "Decision updated", decision.id, old_value, new_value)
    record_decision_version(db, decision, current_user.id)
    db.commit()
    db.refresh(decision)
    return decision


@router.patch(
    "/{decision_id}/status",
    response_model=DecisionResponse,
    summary="Update decision status",
    description="Update the status of a decision to a valid status value.",
)
def update_decision_status(
    decision_id: int,
    status_update: DecisionStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update decision status.
    - **status**: New status (Draft, Under Review, Approved, Rejected, Archived)
    - Only valid status values are accepted
    - Returns 404 if decision not found
    """
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )
    _ensure_can_modify(decision, current_user)
    _ensure_not_archived(decision)

    # Update status with validated enum value
    previous_status = decision.status
    if status_update.status.value not in VALID_STATUS_TRANSITIONS[previous_status]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Invalid status transition from {previous_status} to {status_update.status.value}",
        )
    decision.status = status_update.status.value
    record_activity(
        db, current_user.id, "decision_status_changed", "Decision",
        f"Decision status changed from {previous_status} to {decision.status}", decision.id,
    )
    action = "APPROVE" if decision.status == DecisionStatus.Approved.value else "REJECT" if decision.status == DecisionStatus.Rejected.value else "SUBMIT" if decision.status == DecisionStatus.UnderReview.value else "UPDATE"
    record_audit(db, current_user.id, action, "Decision", f"Decision status changed to {decision.status}", decision.id, {"status": previous_status}, {"status": decision.status})
    record_decision_version(db, decision, current_user.id)

    db.commit()
    db.refresh(decision)
    return decision


@router.delete(
    "/{decision_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a decision",
    description="Delete a decision (soft delete via status change to Archived).",
)
def delete_decision(
    decision_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a decision (archived).
    - Returns 404 if decision not found
    """
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )
    _ensure_can_modify(decision, current_user)

    decision.status = DecisionStatus.Archived.value
    record_activity(db, current_user.id, "decision_archived", "Decision", "Decision archived", decision.id)
    record_audit(db, current_user.id, "DELETE", "Decision", "Decision archived", decision.id, {"status": "previous"}, {"status": decision.status})
    record_decision_version(db, decision, current_user.id)
    db.commit()
    return None


@router.put(
    "/{decision_id}/rationale",
    response_model=DecisionResponse,
    summary="Update decision rationale",
    description="Record or update the rationale for why a decision was made.",
)
def update_decision_rationale(
    decision_id: int,
    rationale_update: DecisionRationaleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update the rationale for a decision.
    - **rationale**: The explanation of why this decision was made
    - Returns 404 if decision not found
    """
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )
    _ensure_can_modify(decision, current_user)
    _ensure_not_archived(decision)

    decision.rationale = rationale_update.rationale
    record_activity(db, current_user.id, "decision_updated", "Decision", "Decision rationale updated", decision.id)
    record_audit(db, current_user.id, "UPDATE", "Decision", "Decision rationale updated", decision.id, {"rationale": None}, {"rationale": decision.rationale})
    record_decision_version(db, decision, current_user.id)
    db.commit()
    db.refresh(decision)
    return decision
