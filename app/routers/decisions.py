from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db

from app.models.activity_log import ActivityLog
from app.models.access_log import AccessLog
from app.models.audit_action import AuditAction
from app.models.audit_entity import AuditEntityType
from app.models.decision import Decision
from app.models.decision_status import DecisionStatus
from app.models.decision_timeline import DecisionTimeline
from app.models.decision_version import DecisionVersion
from app.models.tag import Tag
from app.models.user import User

from app.schemas.activity_log import ActivityLogResponse
from app.schemas.decision import (
    DecisionCreate,
    DecisionResponse,
    DecisionUpdate,
    DecisionStatusUpdate,
    DecisionListResponse,
)
from app.schemas.decision_timeline import DecisionTimelineResponse
from app.schemas.decision_version import DecisionVersionResponse

from app.services.activity_log import create_activity_log
from app.services.audit_log import create_audit_log
from app.services.access_log import create_access_log


router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)


# ==========================================
# CREATE DECISION VERSION
# ==========================================
def create_decision_version(
    db: Session,
    decision: Decision,
    user_id: int
):
    latest_version = (
        db.query(func.max(DecisionVersion.version_number))
        .filter(
            DecisionVersion.decision_id == decision.id
        )
        .scalar()
    )

    next_version_number = (
        latest_version + 1
        if latest_version is not None
        else 1
    )

    version = DecisionVersion(
        decision_id=decision.id,
        version_number=next_version_number,
        title=decision.title,
        problem_statement=decision.problem_statement,
        description=None,
        category=decision.category,
        status=decision.status,
        created_by=user_id
    )

    db.add(version)

    return version


# ==========================================
# CREATE DECISION
# ==========================================
@router.post(
    "",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED
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
        rationale=decision.rationale,
        status=DecisionStatus.DRAFT,
        created_by=current_user.id
    )

    db.add(new_decision)
    db.flush()

    # ------------------------------------------
    # Create initial version
    # ------------------------------------------
    create_decision_version(
        db=db,
        decision=new_decision,
        user_id=current_user.id
    )

    # ------------------------------------------
    # Create timeline event
    # ------------------------------------------
    timeline_event = DecisionTimeline(
        decision_id=new_decision.id,
        event_type="created",
        description="Decision was created"
    )

    db.add(timeline_event)

    # ------------------------------------------
    # Create activity log
    # ------------------------------------------
    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="created",
        entity_type="decision",
        entity_id=new_decision.id,
        description=f"Created decision: {new_decision.title}"
    )

    # ------------------------------------------
    # Create audit log
    # ------------------------------------------
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type=AuditEntityType.DECISION,
        entity_id=new_decision.id,
        description=f"Decision '{new_decision.title}' created",
        new_value={
            "title": new_decision.title,
            "problem_statement": new_decision.problem_statement,
            "category": new_decision.category,
            "rationale": new_decision.rationale,
            "status": new_decision.status.value
        },
        request_method="POST",
        endpoint="/decisions"
    )

    db.commit()
    db.refresh(new_decision)

    return new_decision


# ==========================================
# GET ALL DECISIONS
# FILTERING + SEARCH + SORTING + PAGINATION
# ==========================================
@router.get(
    "",
    response_model=DecisionListResponse
)
def get_decisions(
    status_filter: Optional[DecisionStatus] = Query(
        default=None,
        alias="status"
    ),
    category: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,

    sort_by: str = Query(
        default="newest",
        pattern="^(newest|oldest|updated|title)$"
    ),

    page: int = Query(
        default=1,
        ge=1
    ),

    page_size: int = Query(
        default=10,
        ge=1,
        le=100
    ),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Decision)

    # Filter by status
    if status_filter is not None:
        query = query.filter(
            Decision.status == status_filter
        )

    # Filter by category
    if category is not None:
        query = query.filter(
            Decision.category == category
        )

    # Filter by tag
    if tag is not None:
        query = (
            query
            .join(Decision.tags)
            .filter(Tag.name == tag)
        )

    # Search
    if search is not None:
        search_term = f"%{search}%"

        query = query.filter(
            or_(
                Decision.title.ilike(search_term),
                Decision.problem_statement.ilike(search_term),
                Decision.rationale.ilike(search_term),
            )
        )

    # Sorting
    if sort_by == "newest":
        query = query.order_by(
            Decision.created_at.desc()
        )

    elif sort_by == "oldest":
        query = query.order_by(
            Decision.created_at.asc()
        )

    elif sort_by == "updated":
        query = query.order_by(
            Decision.updated_at.desc()
        )

    elif sort_by == "title":
        query = query.order_by(
            Decision.title.asc()
        )

    query = query.distinct()

    total = query.count()

    items = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # ------------------------------------------
    # Create access log
    # ------------------------------------------
    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="Decision",
        resource_id=0,
        action="LIST"
    )

    db.commit()

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total
    }


# ==========================================
# DEDICATED DECISION SEARCH
# MUST BE BEFORE /{decision_id}
# ==========================================
@router.get(
    "/search",
    response_model=DecisionListResponse
)
def search_decisions(
    q: str = Query(
        ...,
        min_length=1,
        description="Search decisions by title, problem statement, or rationale"
    ),

    page: int = Query(
        default=1,
        ge=1
    ),

    page_size: int = Query(
        default=10,
        ge=1,
        le=100
    ),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    search_term = f"%{q}%"

    query = (
        db.query(Decision)
        .filter(
            or_(
                Decision.title.ilike(search_term),
                Decision.problem_statement.ilike(search_term),
                Decision.rationale.ilike(search_term),
            )
        )
        .order_by(Decision.created_at.desc())
    )

    total = query.count()

    items = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # ------------------------------------------
    # Create access log
    # ------------------------------------------
    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="Decision",
        resource_id=0,
        action="SEARCH"
    )

    db.commit()

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total
    }


# ==========================================
# GET DECISION VERSIONS
# ==========================================
@router.get(
    "/{decision_id}/versions",
    response_model=list[DecisionVersionResponse]
)
def get_decision_versions(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    versions = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision_id
        )
        .order_by(
            DecisionVersion.version_number.asc()
        )
        .all()
    )

    # ------------------------------------------
    # Create access log
    # ------------------------------------------
    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="Decision",
        resource_id=decision_id,
        action="VIEW_VERSIONS"
    )

    db.commit()

    return versions


# ==========================================
# GET SPECIFIC DECISION VERSION
# ==========================================
@router.get(
    "/{decision_id}/versions/{version_number}",
    response_model=DecisionVersionResponse
)
def get_decision_version(
    decision_id: int,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    version = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision_id,
            DecisionVersion.version_number == version_number
        )
        .first()
    )

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision version not found"
        )

    # ------------------------------------------
    # Create access log
    # ------------------------------------------
    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="DecisionVersion",
        resource_id=version.id,
        action="VIEW"
    )

    db.commit()

    return version


# ==========================================
# GET DECISION HISTORY
# ==========================================
@router.get(
    "/{decision_id}/history",
    response_model=list[DecisionVersionResponse]
)
def get_decision_history(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    history = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision_id
        )
        .order_by(
            DecisionVersion.version_number.desc()
        )
        .all()
    )

    # ------------------------------------------
    # Create access log
    # ------------------------------------------
    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="Decision",
        resource_id=decision_id,
        action="VIEW_HISTORY"
    )

    db.commit()

    return history


# ==========================================
# GET DECISION TIMELINE
# ==========================================
@router.get(
    "/{decision_id}/timeline",
    response_model=list[DecisionTimelineResponse]
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

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    timeline = (
        db.query(DecisionTimeline)
        .filter(
            DecisionTimeline.decision_id == decision_id
        )
        .order_by(
            DecisionTimeline.created_at.asc()
        )
        .all()
    )

    # ------------------------------------------
    # Create access log
    # ------------------------------------------
    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="Decision",
        resource_id=decision_id,
        action="VIEW_TIMELINE"
    )

    db.commit()

    return timeline


# ==========================================
# GET ACTIVITY LOGS FOR A SPECIFIC DECISION
# ==========================================
@router.get(
    "/{decision_id}/activity-logs",
    response_model=list[ActivityLogResponse]
)
def get_decision_activity_logs(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    activities = (
        db.query(ActivityLog)
        .filter(
            ActivityLog.entity_type == "decision",
            ActivityLog.entity_id == decision_id
        )
        .order_by(ActivityLog.created_at.asc())
        .all()
    )

    # ------------------------------------------
    # Create access log
    # ------------------------------------------
    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="Decision",
        resource_id=decision_id,
        action="VIEW_ACTIVITY"
    )

    db.commit()

    return activities


# ==========================================
# GET DECISION BY ID
# ==========================================
@router.get(
    "/{decision_id}",
    response_model=DecisionResponse
)
def get_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    # ------------------------------------------
    # Create access log
    # ------------------------------------------
    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="Decision",
        resource_id=decision_id,
        action="VIEW"
    )

    db.commit()

    return decision


# ==========================================
# UPDATE DECISION
# ==========================================
@router.put(
    "/{decision_id}",
    response_model=DecisionResponse
)
def update_decision(
    decision_id: int,
    decision_data: DecisionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    if decision.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this decision"
        )

    updated_fields = []

    # ------------------------------------------
    # Capture OLD values BEFORE modification
    # ------------------------------------------
    old_value = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category,
        "rationale": decision.rationale,
        "status": decision.status.value
    }

    # ------------------------------------------
    # Apply updates
    # ------------------------------------------
    if decision_data.title is not None:
        decision.title = decision_data.title
        updated_fields.append("title")

    if decision_data.problem_statement is not None:
        decision.problem_statement = decision_data.problem_statement
        updated_fields.append("problem statement")

    if decision_data.category is not None:
        decision.category = decision_data.category
        updated_fields.append("category")

    if decision_data.rationale is not None:
        decision.rationale = decision_data.rationale
        updated_fields.append("rationale")

    # ------------------------------------------
    # Only create logs/version if updated
    # ------------------------------------------
    if updated_fields:

        # Create new decision version
        create_decision_version(
            db=db,
            decision=decision,
            user_id=current_user.id
        )

        # Create timeline event
        timeline_event = DecisionTimeline(
            decision_id=decision.id,
            event_type="updated",
            description="Updated: " + ", ".join(updated_fields)
        )

        db.add(timeline_event)

        # Create activity log
        create_activity_log(
            db=db,
            user_id=current_user.id,
            action="updated",
            entity_type="decision",
            entity_id=decision.id,
            description=(
                f"Updated decision: {decision.title} "
                f"({', '.join(updated_fields)})"
            )
        )

        # ------------------------------------------
        # Capture NEW values AFTER modification
        # ------------------------------------------
        new_value = {
            "title": decision.title,
            "problem_statement": decision.problem_statement,
            "category": decision.category,
            "rationale": decision.rationale,
            "status": decision.status.value
        }

        # ------------------------------------------
        # Create audit log
        # ------------------------------------------
        create_audit_log(
            db=db,
            user_id=current_user.id,
            action=AuditAction.UPDATE,
            entity_type=AuditEntityType.DECISION,
            entity_id=decision.id,
            description=(
                f"Decision '{decision.title}' updated: "
                f"{', '.join(updated_fields)}"
            ),
            old_value=old_value,
            new_value=new_value,
            request_method="PUT",
            endpoint=f"/decisions/{decision.id}"
        )

    db.commit()
    db.refresh(decision)

    return decision


# ==========================================
# UPDATE DECISION STATUS
# ==========================================
@router.patch(
    "/{decision_id}/status",
    response_model=DecisionResponse
)
def update_decision_status(
    decision_id: int,
    status_data: DecisionStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    if decision.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this decision status"
        )

    old_status = decision.status
    new_status = status_data.status

    # Prevent duplicate status update
    if old_status == new_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Decision is already in {new_status.value} status"
        )

    # ------------------------------------------
    # Change status
    # ------------------------------------------
    decision.status = new_status

    # ------------------------------------------
    # Create new decision version
    # ------------------------------------------
    create_decision_version(
        db=db,
        decision=decision,
        user_id=current_user.id
    )

    # ------------------------------------------
    # Create timeline event
    # ------------------------------------------
    timeline_event = DecisionTimeline(
        decision_id=decision.id,
        event_type="status_changed",
        description=(
            f"Status changed from "
            f"{old_status.value} to {new_status.value}"
        )
    )

    db.add(timeline_event)

    # ------------------------------------------
    # Create activity log
    # ------------------------------------------
    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="status_changed",
        entity_type="decision",
        entity_id=decision.id,
        description=(
            f"Changed decision status from "
            f"{old_status.value} to {new_status.value}: "
            f"{decision.title}"
        )
    )

    # ------------------------------------------
    # Determine audit action
    # ------------------------------------------
    if new_status == DecisionStatus.APPROVED:
        audit_action = AuditAction.APPROVE

    elif new_status == DecisionStatus.REJECTED:
        audit_action = AuditAction.REJECT

    elif new_status == DecisionStatus.UNDER_REVIEW:
        audit_action = AuditAction.SUBMIT

    elif new_status == DecisionStatus.ARCHIVED:
        audit_action = AuditAction.ARCHIVE

    else:
        audit_action = AuditAction.UPDATE

    # ------------------------------------------
    # Create audit log
    # ------------------------------------------
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=audit_action,
        entity_type=AuditEntityType.DECISION,
        entity_id=decision.id,
        description=(
            f"Decision status changed from "
            f"{old_status.value} to {new_status.value}"
        ),
        old_value={
            "status": old_status.value
        },
        new_value={
            "status": new_status.value
        },
        request_method="PATCH",
        endpoint=f"/decisions/{decision.id}/status"
    )

    db.commit()
    db.refresh(decision)

    return decision