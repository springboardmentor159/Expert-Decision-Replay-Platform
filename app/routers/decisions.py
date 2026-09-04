from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status as http_status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.alternative import Alternative
from app.models.approval import Approval
from app.models.audit_log import AuditLog
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.decision_version import DecisionVersion
from app.models.discussion_thread import DiscussionThread
from app.models.meeting_note import MeetingNote
from app.models.tag import Tag
from app.models.user import User
from app.schemas.decision import (
    DecisionCreate,
    DecisionHistoryItem,
    DecisionHistoryResponse,
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
from app.schemas.decision_version import DecisionVersionListItem, DecisionVersionResponse
from app.schemas.tag import DecisionTagAssign, TagResponse
from app.services.activity_logger import log_activity
from app.services.audit_service import (
    create_decision_version,
    get_client_ip,
    log_access_event,
    log_audit,
)

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
    request: Request,
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

    # 1. Create Initial Version (Version 1)
    create_decision_version(
        db=db,
        decision=new_decision,
        created_by=current_user.id
    )

    # 2. Log Audit record
    client_ip = get_client_ip(request)
    log_audit(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Decision",
        entity_id=new_decision.id,
        description=f"User {current_user.full_name} created decision '{new_decision.title}'",
        new_value={
            "title": new_decision.title,
            "problem_statement": new_decision.problem_statement,
            "category": new_decision.category,
            "status": new_decision.status
        },
        ip_address=client_ip,
        request_method=request.method,
        endpoint=str(request.url.path)
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
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    # Log access event
    client_ip = get_client_ip(request)
    log_access_event(
        db=db,
        user_id=current_user.id,
        resource_type="Decision",
        resource_id=decision.id,
        action="VIEW",
        ip_address=client_ip
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
    request: Request,
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

    old_value = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category
    }

    decision.title = decision_update.title
    decision.problem_statement = decision_update.problem_statement
    decision.category = decision_update.category
    decision.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(decision)

    new_value = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category
    }

    # Create next sequential version
    create_decision_version(
        db=db,
        decision=decision,
        created_by=current_user.id
    )

    client_ip = get_client_ip(request)
    log_audit(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"User {current_user.full_name} updated decision '{decision.title}'",
        old_value=old_value,
        new_value=new_value,
        ip_address=client_ip,
        request_method=request.method,
        endpoint=str(request.url.path)
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
    request: Request,
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

    # Strict Decision State Machine
    VALID_TRANSITIONS = {
        "Draft": {"Under Review", "Archived"},
        "Under Review": {"Draft", "Approved", "Rejected", "Archived"},
        "Approved": {"Archived"},
        "Rejected": {"Draft", "Archived"},
        "Archived": set(),  # Terminal state
    }

    if old_status == "Archived":
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify an archived decision"
        )

    if new_status != old_status and new_status not in VALID_TRANSITIONS.get(old_status, set()):
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid state transition from '{old_status}' to '{new_status}'. Allowed target states: {sorted(list(VALID_TRANSITIONS.get(old_status, set())))}"
        )

    decision.status = new_status
    decision.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(decision)

    # Create next version upon major status change
    create_decision_version(
        db=db,
        decision=decision,
        created_by=current_user.id
    )

    action_name = "SUBMIT" if new_status == "Under Review" else "UPDATE"
    client_ip = get_client_ip(request)

    log_audit(
        db=db,
        user_id=current_user.id,
        action=action_name,
        entity_type="Decision",
        entity_id=decision.id,
        description=f"User {current_user.full_name} changed status of decision '{decision.title}' from '{old_status}' to '{new_status}'",
        old_value={"status": old_status},
        new_value={"status": new_status},
        ip_address=client_ip,
        request_method=request.method,
        endpoint=str(request.url.path)
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
    request: Request,
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

    old_rationale = decision.rationale
    decision.rationale = rationale_update.rationale
    decision.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(decision)

    client_ip = get_client_ip(request)
    log_audit(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"User {current_user.full_name} recorded rationale for decision '{decision.title}'",
        old_value={"rationale": old_rationale},
        new_value={"rationale": decision.rationale},
        ip_address=client_ip,
        request_method=request.method,
        endpoint=str(request.url.path)
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
# DECISION VERSIONS API
# =============================================================================

@router.get(
    "/{decision_id}/versions",
    response_model=List[DecisionVersionListItem],
    summary="Get all versions of a decision"
)
def get_decision_versions(
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

    versions = (
        db.query(DecisionVersion)
        .filter(DecisionVersion.decision_id == decision_id)
        .order_by(DecisionVersion.version_number.asc())
        .all()
    )
    return versions


@router.get(
    "/{decision_id}/versions/{version_number}",
    response_model=DecisionVersionResponse,
    summary="Get specific version snapshot of a decision"
)
def get_specific_decision_version(
    decision_id: int,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    version_record = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision_id,
            DecisionVersion.version_number == version_number
        )
        .first()
    )
    if not version_record:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Decision version {version_number} not found"
        )

    return version_record


# =============================================================================
# DECISION CHANGE HISTORY API
# =============================================================================

@router.get(
    "/{decision_id}/history",
    response_model=DecisionHistoryResponse,
    summary="Get chronological change history for a decision and related entities"
)
def get_decision_history(
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

    # Collect IDs for related entities to capture full decision lifecycle
    alt_ids = [a.id for a in decision.alternatives]
    comment_ids = [c.id for c in decision.comments]
    thread_ids = [t.id for t in decision.threads]
    note_ids = [n.id for n in decision.meeting_notes]
    approval_ids = [ap.id for ap in decision.approvals]

    # Query audit logs for Decision and its sub-entities
    filters = [
        (AuditLog.entity_type == "Decision") & (AuditLog.entity_id == decision_id)
    ]
    if alt_ids:
        filters.append((AuditLog.entity_type == "Alternative") & (AuditLog.entity_id.in_(alt_ids)))
    if comment_ids:
        filters.append((AuditLog.entity_type == "Comment") & (AuditLog.entity_id.in_(comment_ids)))
    if thread_ids:
        filters.append((AuditLog.entity_type == "DiscussionThread") & (AuditLog.entity_id.in_(thread_ids)))
    if note_ids:
        filters.append((AuditLog.entity_type == "MeetingNote") & (AuditLog.entity_id.in_(note_ids)))
    if approval_ids:
        filters.append((AuditLog.entity_type == "Approval") & (AuditLog.entity_id.in_(approval_ids)))

    audit_logs = db.query(AuditLog).filter(or_(*filters)).order_by(AuditLog.created_at.asc()).all()

    history_items: List[DecisionHistoryItem] = []
    for log in audit_logs:
        history_items.append(
            DecisionHistoryItem(
                id=log.id,
                action=log.action,
                event_type=f"{log.entity_type} {log.action.capitalize()}",
                entity_type=log.entity_type,
                entity_id=log.entity_id,
                user_id=log.user_id,
                user_name=log.user.full_name if log.user else None,
                description=log.description,
                old_value=log.old_value,
                new_value=log.new_value,
                timestamp=log.created_at
            )
        )

    return DecisionHistoryResponse(
        decision_id=decision.id,
        title=decision.title,
        total_events=len(history_items),
        history=history_items
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
    request: Request,
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
    client_ip = get_client_ip(request)
    log_audit(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"User {current_user.full_name} assigned tags [{tag_names}] to Decision #{decision.id}",
        new_value={"tags": [t.name for t in decision.tags]},
        ip_address=client_ip,
        request_method=request.method,
        endpoint=str(request.url.path)
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
    request: Request,
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

    client_ip = get_client_ip(request)
    log_audit(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"User {current_user.full_name} removed tag '{tag_to_remove.name}' from Decision #{decision.id}",
        ip_address=client_ip,
        request_method=request.method,
        endpoint=str(request.url.path)
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
