from datetime import datetime
from typing import Any, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.activity_log import ActivityLog
from app.models.alternative import Alternative
from app.models.approval import Approval
from app.models.audit_log import AuditLog
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.decision_version import DecisionVersion
from app.models.discussion_thread import DiscussionThread
from app.models.meeting_note import MeetingNote
from app.models.tag import Tag, decision_tags
from app.models.user import User
from app.schemas.decision import (
    DecisionCategory,
    DecisionCreate,
    DecisionRationaleResponse,
    DecisionRationaleUpdate,
    DecisionResponse,
    DecisionStatus,
    DecisionStatusUpdate,
    DecisionTimelineEvent,
    DecisionTimelineResponse,
    DecisionUpdate,
    PaginatedDecisionsResponse,
)
from app.schemas.decision_version import (
    DecisionHistoryItem,
    DecisionHistoryResponse,
    DecisionVersionResponse,
)
from app.schemas.tag import TagAssign, TagSimpleResponse
from app.services.activity_logger import log_activity
from app.services.audit_service import (
    create_decision_version,
    log_access_event,
    log_audit,
)

VALID_CATEGORIES = {
    "Technology",
    "Finance",
    "Operations",
    "Human Resources",
    "Security",
    "Product",
    "Infrastructure",
    "Strategy",
    "Architecture",
}

ALLOWED_SORT_FIELDS = {"created_at", "updated_at", "title", "status", "category"}

router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)


def _validate_category(category_name: str) -> str:
    """Validate category against controlled list or ensure non-empty normalized string"""
    if not category_name or not category_name.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Category cannot be empty"
        )
    cat_clean = category_name.strip()
    for valid in VALID_CATEGORIES:
        if valid.lower() == cat_clean.lower():
            return valid
    return cat_clean


def _to_version_response(ver: DecisionVersion) -> DecisionVersionResponse:
    return DecisionVersionResponse(
        id=ver.id,
        decision_id=ver.decision_id,
        version_number=ver.version_number,
        title=ver.title,
        problem_statement=ver.problem_statement,
        description=ver.description,
        category=ver.category,
        status=ver.status,
        created_by=ver.created_by,
        created_by_name=ver.creator.full_name if ver.creator else None,
        created_at=ver.created_at,
    )


# --- 1. DECISION SEARCH (Sprint 9) ---
@router.get(
    "/search",
    response_model=PaginatedDecisionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Search decisions with keyword, category, status, and tag filters"
)
def search_decisions(
    q: Optional[str] = Query(None, description="Search keyword in title, problem statement, rationale"),
    category: Optional[str] = Query(None, description="Category filter"),
    status_filter: Optional[str] = Query(None, alias="status", description="Status filter"),
    tag: Optional[str] = Query(None, description="Tag filter"),
    sort: Optional[str] = Query("created_at", description="Sort column (created_at, updated_at, title, category, status)"),
    order: Optional[str] = Query("desc", description="Sort order (asc, desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if sort not in ALLOWED_SORT_FIELDS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid sort field '{sort}'. Allowed: {', '.join(sorted(ALLOWED_SORT_FIELDS))}"
        )

    order_lower = order.lower() if order else "desc"
    if order_lower not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Order must be 'asc' or 'desc'"
        )

    query = db.query(Decision)

    if q and q.strip():
        term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Decision.title.ilike(term),
                Decision.problem_statement.ilike(term),
                Decision.rationale.ilike(term)
            )
        )

    if category and category.strip():
        query = query.filter(func.lower(Decision.category) == func.lower(category.strip()))

    if status_filter and status_filter.strip():
        valid_statuses = {s.value.lower(): s.value for s in DecisionStatus}
        if status_filter.strip().lower() not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid status '{status_filter}'. Allowed: {', '.join([s.value for s in DecisionStatus])}"
            )
        actual_status = valid_statuses[status_filter.strip().lower()]
        query = query.filter(Decision.status == actual_status)

    if tag and tag.strip():
        query = query.join(Decision.tags).filter(func.lower(Tag.name) == func.lower(tag.strip()))

    total = query.distinct().count()

    sort_col = getattr(Decision, sort)
    if order_lower == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    items = query.distinct().offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedDecisionsResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        results=items
    )


# --- 2. CREATE DECISION ---
@router.post(
    "",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new decision (Automatic Version 1 and Audit Log)"
)
def create_decision(
    decision: DecisionCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    validated_cat = _validate_category(decision.category)

    new_decision = Decision(
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=validated_cat,
        status="Draft",
        created_by=current_user.id
    )
    db.add(new_decision)
    db.commit()
    db.refresh(new_decision)

    # Automatically create initial Version 1 snapshot
    create_decision_version(
        db=db,
        decision=new_decision,
        user_id=current_user.id,
        description="Initial version upon decision creation"
    )

    # Automatic Audit Logging
    client_ip = request.client.host if request.client else None
    new_snapshot = {
        "title": new_decision.title,
        "problem_statement": new_decision.problem_statement,
        "category": new_decision.category,
        "status": new_decision.status
    }
    log_audit(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Decision",
        entity_id=new_decision.id,
        description=f"Decision '{new_decision.title}' created in category '{validated_cat}'",
        ip_address=client_ip,
        old_value=None,
        new_value=new_snapshot,
        request_method="POST",
        endpoint="/decisions"
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="create_decision",
        entity_type="decision",
        entity_id=new_decision.id,
        description=f"User {current_user.full_name} created decision '{new_decision.title}' in category '{validated_cat}'"
    )

    return new_decision


# --- 3. GET DECISIONS (Supports List and Optional Pagination / Filtering) ---
@router.get(
    "",
    response_model=Union[PaginatedDecisionsResponse, List[DecisionResponse]],
    summary="Get decisions with optional query filters and pagination"
)
def get_decisions(
    status_filter: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query("created_at"),
    order: Optional[str] = Query("desc"),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if sort and sort not in ALLOWED_SORT_FIELDS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid sort field '{sort}'. Allowed: {', '.join(sorted(ALLOWED_SORT_FIELDS))}"
        )

    order_lower = order.lower() if order else "desc"
    if order_lower not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Order must be 'asc' or 'desc'"
        )

    query = db.query(Decision)

    if q and q.strip():
        term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Decision.title.ilike(term),
                Decision.problem_statement.ilike(term),
                Decision.rationale.ilike(term)
            )
        )

    if status_filter and status_filter.strip():
        valid_statuses = {s.value.lower(): s.value for s in DecisionStatus}
        if status_filter.strip().lower() not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid status '{status_filter}'. Allowed: {', '.join([s.value for s in DecisionStatus])}"
            )
        actual_status = valid_statuses[status_filter.strip().lower()]
        query = query.filter(Decision.status == actual_status)

    if category and category.strip():
        query = query.filter(func.lower(Decision.category) == func.lower(category.strip()))

    if tag and tag.strip():
        query = query.join(Decision.tags).filter(func.lower(Tag.name) == func.lower(tag.strip()))

    sort_col = getattr(Decision, sort if sort else "created_at")
    if order_lower == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    if page is not None and page_size is not None:
        total = query.distinct().count()
        items = query.distinct().offset((page - 1) * page_size).limit(page_size).all()
        return PaginatedDecisionsResponse(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            results=items
        )

    return query.distinct().all()


# --- 4. GET DECISION BY ID (Access Tracked) ---
@router.get(
    "/{decision_id}",
    response_model=DecisionResponse,
    summary="Get single decision by ID (Access Tracked)"
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    # Automatic Access Logging
    client_ip = request.client.host if request.client else None
    log_access_event(
        db=db,
        user_id=current_user.id,
        resource_type="Decision",
        resource_id=decision.id,
        action="VIEW",
        ip_address=client_ip
    )

    return decision


# --- 5. UPDATE DECISION (Automatic Versioning & Audit Diff) ---
@router.put(
    "/{decision_id}",
    response_model=DecisionResponse,
    summary="Update decision details (Automatic Version Increment & Audit Diff)"
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    if decision.created_by != current_user.id and current_user.role not in ["Administrator", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this decision"
        )

    if decision.status == "Archived" and current_user.role not in ["Administrator", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify an archived decision"
        )

    validated_cat = _validate_category(decision_update.category)

    old_snapshot = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category
    }

    decision.title = decision_update.title
    decision.problem_statement = decision_update.problem_statement
    decision.category = validated_cat

    db.commit()
    db.refresh(decision)

    new_snapshot = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category
    }

    # Automatically create new Decision Version
    create_decision_version(
        db=db,
        decision=decision,
        user_id=current_user.id,
        description=f"Updated by {current_user.full_name}"
    )

    # Automatic Audit Logging
    client_ip = request.client.host if request.client else None
    log_audit(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"Decision '{decision.title}' updated by {current_user.full_name}",
        ip_address=client_ip,
        old_value=old_snapshot,
        new_value=new_snapshot,
        request_method="PUT",
        endpoint=f"/decisions/{decision.id}"
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="update_decision",
        entity_type="decision",
        entity_id=decision.id,
        description=f"User {current_user.full_name} updated decision '{decision.title}'"
    )

    return decision


# --- 6. UPDATE DECISION STATUS (Automatic Versioning & Audit Diff) ---
@router.patch(
    "/{decision_id}/status",
    response_model=DecisionResponse,
    summary="Update decision status (Automatic Version Increment & Audit Diff)"
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    if decision.created_by != current_user.id and current_user.role not in ["Administrator", "Manager", "Reviewer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update the status of this decision"
        )

    old_status = decision.status
    new_status = status_update.status.value

    VALID_STATE_TRANSITIONS = {
        "Draft": {"Draft", "Under Review", "Approved", "Archived"},
        "Under Review": {"Under Review", "Approved", "Rejected", "Draft", "Archived"},
        "Approved": {"Approved", "Archived"},
        "Rejected": {"Rejected", "Draft", "Archived"},
        "Archived": {"Archived"},
    }

    allowed_targets = VALID_STATE_TRANSITIONS.get(old_status, set())
    if new_status not in allowed_targets:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid state transition from '{old_status}' to '{new_status}'"
        )

    old_snapshot = {"status": old_status}
    decision.status = new_status
    db.commit()
    db.refresh(decision)

    new_snapshot = {"status": new_status}

    # Automatically create new Decision Version
    create_decision_version(
        db=db,
        decision=decision,
        user_id=current_user.id,
        description=f"Status changed from '{old_status}' to '{new_status}'"
    )

    # Automatic Audit Logging
    client_ip = request.client.host if request.client else None
    log_audit(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"Decision status changed from '{old_status}' to '{new_status}' by {current_user.full_name}",
        ip_address=client_ip,
        old_value=old_snapshot,
        new_value=new_snapshot,
        request_method="PATCH",
        endpoint=f"/decisions/{decision.id}/status"
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="update_decision_status",
        entity_type="decision",
        entity_id=decision.id,
        description=f"User {current_user.full_name} changed decision status from '{old_status}' to '{new_status}'"
    )

    return decision


# --- 7. UPDATE DECISION RATIONALE ---
@router.put(
    "/{decision_id}/rationale",
    response_model=DecisionResponse,
    status_code=status.HTTP_200_OK,
    summary="Record or update decision rationale (Automatic Version & Audit)"
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    if decision.created_by != current_user.id and current_user.role not in ["Administrator", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update rationale for this decision"
        )

    old_snapshot = {"rationale": decision.rationale}
    decision.rationale = rationale_update.rationale
    db.commit()
    db.refresh(decision)

    new_snapshot = {"rationale": decision.rationale}

    # Automatically create new Decision Version
    create_decision_version(
        db=db,
        decision=decision,
        user_id=current_user.id,
        description=f"Rationale updated by {current_user.full_name}"
    )

    # Automatic Audit Logging
    client_ip = request.client.host if request.client else None
    log_audit(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"Rationale updated for decision '{decision.title}'",
        ip_address=client_ip,
        old_value=old_snapshot,
        new_value=new_snapshot,
        request_method="PUT",
        endpoint=f"/decisions/{decision.id}/rationale"
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="update_rationale",
        entity_type="decision",
        entity_id=decision.id,
        description=f"User {current_user.full_name} updated rationale for decision '{decision.title}'"
    )

    return decision


# --- 8. GET DECISION RATIONALE ---
@router.get(
    "/{decision_id}/rationale",
    response_model=DecisionRationaleResponse,
    status_code=status.HTTP_200_OK,
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return DecisionRationaleResponse(
        decision_id=decision.id,
        rationale=decision.rationale
    )


# --- 9. ASSIGN TAGS TO DECISION ---
@router.post(
    "/{decision_id}/tags",
    response_model=List[TagSimpleResponse],
    status_code=status.HTTP_200_OK,
    summary="Assign tags to a decision"
)
def assign_tags_to_decision(
    decision_id: int,
    tag_in: TagAssign,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    if decision.created_by != current_user.id and current_user.role not in ["Administrator", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify tags for this decision"
        )

    tags = db.query(Tag).filter(Tag.id.in_(tag_in.tag_ids)).all()
    if len(tags) != len(set(tag_in.tag_ids)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more specified tags do not exist"
        )

    existing_tag_ids = {t.id for t in decision.tags}
    for tag in tags:
        if tag.id not in existing_tag_ids:
            decision.tags.append(tag)

    db.commit()
    db.refresh(decision)

    tag_names = ", ".join([t.name for t in tags])
    client_ip = request.client.host if request.client else None
    log_audit(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"Assigned tags [{tag_names}] to decision '{decision.title}'",
        ip_address=client_ip,
        old_value=None,
        new_value={"tags": [t.name for t in decision.tags]},
        request_method="POST",
        endpoint=f"/decisions/{decision.id}/tags"
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="assign_tags",
        entity_type="decision",
        entity_id=decision.id,
        description=f"User {current_user.full_name} assigned tags [{tag_names}] to decision '{decision.title}'"
    )

    return [TagSimpleResponse(id=t.id, name=t.name) for t in decision.tags]


# --- 10. GET DECISION TAGS ---
@router.get(
    "/{decision_id}/tags",
    response_model=List[TagSimpleResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all tags assigned to a decision"
)
def get_decision_tags(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return [TagSimpleResponse(id=t.id, name=t.name) for t in decision.tags]


# --- 11. REMOVE TAG FROM DECISION ---
@router.delete(
    "/{decision_id}/tags/{tag_id}",
    status_code=status.HTTP_200_OK,
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    if decision.created_by != current_user.id and current_user.role not in ["Administrator", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify tags for this decision"
        )

    tag_to_remove = None
    for t in decision.tags:
        if t.id == tag_id:
            tag_to_remove = t
            break

    if not tag_to_remove:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not associated with this decision"
        )

    decision.tags.remove(tag_to_remove)
    db.commit()

    client_ip = request.client.host if request.client else None
    log_audit(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"Removed tag '{tag_to_remove.name}' from decision '{decision.title}'",
        ip_address=client_ip,
        old_value={"removed_tag": tag_to_remove.name},
        new_value={"tags": [t.name for t in decision.tags]},
        request_method="DELETE",
        endpoint=f"/decisions/{decision.id}/tags/{tag_id}"
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="remove_tag",
        entity_type="decision",
        entity_id=decision.id,
        description=f"User {current_user.full_name} removed tag '{tag_to_remove.name}' from decision '{decision.title}'"
    )

    return {"message": f"Tag '{tag_to_remove.name}' removed from decision successfully"}


# --- 12. DECISION VERSIONS API (Sprint 11 Requirement) ---
@router.get(
    "/{decision_id}/versions",
    response_model=List[DecisionVersionResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all historical versions for a decision"
)
def get_decision_versions(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    versions = (
        db.query(DecisionVersion)
        .filter(DecisionVersion.decision_id == decision_id)
        .order_by(DecisionVersion.version_number.asc())
        .all()
    )

    return [_to_version_response(v) for v in versions]


@router.get(
    "/{decision_id}/versions/{version_number}",
    response_model=DecisionVersionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a specific historical version of a decision"
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
            status_code=status.HTTP_404_NOT_FOUND,
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_number} not found for decision {decision_id}"
        )

    return _to_version_response(version_record)


# --- 13. DECISION CHANGE HISTORY API (Sprint 11 Requirement) ---
@router.get(
    "/{decision_id}/history",
    response_model=DecisionHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get chronological change history and audit trail for a decision"
)
def get_decision_history(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    # Collect sub-entity IDs associated with this decision
    alt_ids = [a.id for a in decision.alternatives]
    comm_ids = [c.id for c in decision.comments]
    thread_ids = [t.id for t in decision.threads]
    mn_ids = [m.id for m in decision.meeting_notes]
    apprv_ids = [ap.id for ap in decision.approvals]

    # Query audit logs for Decision and related child entities
    history_query = db.query(AuditLog).filter(
        or_(
            (AuditLog.entity_type == "Decision") & (AuditLog.entity_id == decision_id),
            (AuditLog.entity_type == "Alternative") & (AuditLog.entity_id.in_(alt_ids) if alt_ids else False),
            (AuditLog.entity_type == "Comment") & (AuditLog.entity_id.in_(comm_ids) if comm_ids else False),
            (AuditLog.entity_type == "DiscussionThread") & (AuditLog.entity_id.in_(thread_ids) if thread_ids else False),
            (AuditLog.entity_type == "MeetingNote") & (AuditLog.entity_id.in_(mn_ids) if mn_ids else False),
            (AuditLog.entity_type == "Approval") & (AuditLog.entity_id.in_(apprv_ids) if apprv_ids else False),
        )
    ).order_by(AuditLog.created_at.asc()).all()

    history_items: List[DecisionHistoryItem] = []
    for log in history_query:
        history_items.append(
            DecisionHistoryItem(
                id=log.id,
                timestamp=log.created_at,
                action=log.action,
                entity_type=log.entity_type,
                entity_id=log.entity_id,
                description=log.description,
                user_id=log.user_id,
                user_name=log.user.full_name if log.user else None,
                old_value=log.old_value,
                new_value=log.new_value
            )
        )

    return DecisionHistoryResponse(
        decision_id=decision.id,
        decision_title=decision.title,
        total_events=len(history_items),
        history=history_items
    )


# --- 14. DECISION TIMELINE (Sprint 9) ---
@router.get(
    "/{decision_id}/timeline",
    response_model=DecisionTimelineResponse,
    status_code=status.HTTP_200_OK,
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    events: List[DecisionTimelineEvent] = []

    # 1. Decision Creation
    events.append(
        DecisionTimelineEvent(
            event_type="Decision created",
            description=f"Decision '{decision.title}' created in category '{decision.category}'",
            user_id=decision.created_by,
            user_name=decision.creator.full_name if decision.creator else None,
            timestamp=decision.created_at
        )
    )

    # 2. Alternatives
    for alt in decision.alternatives:
        events.append(
            DecisionTimelineEvent(
                id=alt.id,
                event_type="Alternative created",
                description=f"Alternative '{alt.name}' added (Risk: {alt.risk_level}, Feasibility: {alt.feasibility_score})",
                timestamp=alt.created_at
            )
        )

    # 3. Comments
    for com in decision.comments:
        events.append(
            DecisionTimelineEvent(
                id=com.id,
                event_type="Comment added",
                description=f"Comment added: {com.content[:60]}...",
                user_id=com.user_id,
                user_name=com.author.full_name if com.author else None,
                timestamp=com.created_at
            )
        )

    # 4. Discussion Threads
    for th in decision.threads:
        events.append(
            DecisionTimelineEvent(
                id=th.id,
                event_type="Discussion thread created",
                description=f"Discussion thread '{th.title}' opened",
                user_id=th.created_by,
                user_name=th.creator.full_name if th.creator else None,
                timestamp=th.created_at
            )
        )

    # 5. Meeting Notes
    for mn in decision.meeting_notes:
        events.append(
            DecisionTimelineEvent(
                id=mn.id,
                event_type="Meeting note added",
                description=f"Meeting note '{mn.title}' recorded",
                user_id=mn.created_by,
                user_name=mn.creator.full_name if mn.creator else None,
                timestamp=mn.meeting_date if mn.meeting_date else mn.created_at
            )
        )

    # 6. Approvals
    for apprv in decision.approvals:
        events.append(
            DecisionTimelineEvent(
                id=apprv.id,
                event_type="Approval assigned",
                description=f"Approval assigned to reviewer (Level {apprv.approval_level}, Status: {apprv.status})",
                user_id=apprv.reviewer_id,
                user_name=apprv.reviewer.full_name if apprv.reviewer else None,
                timestamp=apprv.created_at
            )
        )
        if apprv.completed_at:
            events.append(
                DecisionTimelineEvent(
                    id=apprv.id,
                    event_type=f"Decision {apprv.status.lower()}",
                    description=f"Decision {apprv.status} by reviewer: {apprv.comments or 'No comments'}",
                    user_id=apprv.reviewer_id,
                    user_name=apprv.reviewer.full_name if apprv.reviewer else None,
                    timestamp=apprv.completed_at
                )
            )

    # 7. Activity logs for this decision
    act_logs = db.query(ActivityLog).filter(
        ActivityLog.entity_type == "decision",
        ActivityLog.entity_id == decision_id
    ).all()
    logged_actions = {"update_decision", "update_decision_status", "update_rationale", "assign_tags", "remove_tag"}
    for al in act_logs:
        if al.action in logged_actions:
            events.append(
                DecisionTimelineEvent(
                    id=al.id,
                    event_type=al.action.replace("_", " ").title(),
                    description=al.description,
                    user_id=al.user_id,
                    user_name=al.user.full_name if al.user else None,
                    timestamp=al.created_at
                )
            )

    events.sort(key=lambda x: x.timestamp)

    return DecisionTimelineResponse(
        decision_id=decision.id,
        decision_title=decision.title,
        current_status=decision.status,
        events=events
    )
