from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, asc, desc

from app.core.activity_logger import create_activity_log
from app.core.audit_logger import create_audit_log
from app.core.dependencies import get_current_user, require_admin
from app.db.database import get_db

from app.models.decision import Decision
from app.models.alternative import Alternative
from app.models.tag import Tag
from app.models.user import User
from app.models.decision_version import DecisionVersion
from app.models.audit_log import AuditLog

from app.schemas.decision import (
    DecisionCreate,
    DecisionUpdate,
    DecisionStatusUpdate,
    DecisionResponse,
    DecisionStatus,
    DecisionRationaleUpdate,
)

from app.schemas.tag import (
    AssignTagsRequest,
    TagResponse,
)


router = APIRouter(
    prefix="/decisions",
    tags=["Decision Management"]
)


# =========================================================
# CREATE DECISION
# =========================================================

@router.post(
    "",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_decision(
    decision_data: DecisionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    decision = Decision(
        title=decision_data.title,
        problem_statement=decision_data.problem_statement,
        category=decision_data.category,
        status=DecisionStatus.DRAFT.value,
        created_by=current_user.id
    )

    db.add(decision)
    db.commit()
    db.refresh(decision)

    # Create Version 1
    first_version = DecisionVersion(
        decision_id=decision.id,
        version_number=1,
        title=decision.title,
        problem_statement=decision.problem_statement,
        description=None,
        category=decision.category,
        status=decision.status,
        created_by=current_user.id
    )

    db.add(first_version)
    db.commit()
    db.refresh(first_version)

    # Activity log
    create_activity_log(
        db=db,
        user=current_user,
        action="CREATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"Created decision: {decision.title}"
    )

    # Audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"Created decision: {decision.title}",
        old_value=None,
        new_value={
            "title": decision.title,
            "problem_statement": decision.problem_statement,
            "category": decision.category,
            "status": decision.status
        }
    )

    return decision


# =========================================================
# GET ALL DECISIONS
# SEARCH + STATUS + CATEGORY + TAG
# PAGINATION + SORTING
# =========================================================

@router.get(
    "",
    response_model=list[DecisionResponse]
)
def get_decisions(
    search: str | None = Query(
        default=None,
        description="Search by decision title or problem statement"
    ),
    status_filter: DecisionStatus | None = Query(
        default=None,
        alias="status"
    ),
    category: str | None = Query(
        default=None
    ),
    tag: str | None = Query(
        default=None,
        description="Filter decisions by tag name"
    ),
    page: int = Query(
        default=1,
        ge=1
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100
    ),
    sort_by: str = Query(
        default="created_at",
        description="Allowed values: created_at, updated_at, title"
    ),
    order: str = Query(
        default="desc",
        description="Allowed values: asc, desc"
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    query = db.query(Decision)

    # Keyword search
    if search:
        search_pattern = f"%{search}%"

        query = query.filter(
            or_(
                Decision.title.ilike(search_pattern),
                Decision.problem_statement.ilike(search_pattern)
            )
        )

    # Status filter
    if status_filter:
        query = query.filter(
            Decision.status == status_filter.value
        )

    # Category filter
    if category:
        query = query.filter(
            Decision.category == category
        )

    # Tag filter
    if tag:
        query = query.join(
            Decision.tags
        ).filter(
            Tag.name == tag
        )

    # Controlled sorting
    allowed_sort_fields = {
        "created_at": Decision.created_at,
        "updated_at": Decision.updated_at,
        "title": Decision.title,
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Invalid sort field. "
                "Allowed values: created_at, updated_at, title"
            )
        )

    if order.lower() not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid order. Allowed values: asc, desc"
        )

    sort_column = allowed_sort_fields[sort_by]

    if order.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    # Pagination
    offset = (page - 1) * limit

    query = query.offset(offset).limit(limit)

    return query.all()


# =========================================================
# DECISION SEARCH
# =========================================================

@router.get(
    "/search"
)
def search_decisions(
    q: str = Query(
        ...,
        min_length=1,
        description="Search in title, problem statement and rationale"
    ),
    category: str | None = Query(
        default=None
    ),
    status_filter: DecisionStatus | None = Query(
        default=None,
        alias="status"
    ),
    tag: str | None = Query(
        default=None
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    search_pattern = f"%{q}%"

    query = (
        db.query(Decision)
        .filter(
            or_(
                Decision.title.ilike(search_pattern),
                Decision.problem_statement.ilike(search_pattern),
                Decision.rationale.ilike(search_pattern)
            )
        )
    )

    if category:
        query = query.filter(
            Decision.category == category
        )

    if status_filter:
        query = query.filter(
            Decision.status == status_filter.value
        )

    if tag:
        query = query.join(
            Decision.tags
        ).filter(
            Tag.name == tag
        )

    decisions = query.all()

    return {
        "results": [
            {
                "id": decision.id,
                "title": decision.title,
                "category": decision.category,
                "status": decision.status,
                "tags": [
                    tag.name
                    for tag in decision.tags
                ],
                "created_at": decision.created_at,
                "updated_at": decision.updated_at
            }
            for decision in decisions
        ]
    }


# =========================================================
# COMPARE DECISION ALTERNATIVES
# =========================================================

@router.get(
    "/{decision_id}/alternatives/compare"
)
def compare_alternatives(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Check whether decision exists
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

    # Get all alternatives belonging to this decision
    alternatives = (
        db.query(Alternative)
        .filter(
            Alternative.decision_id == decision_id
        )
        .order_by(
            Alternative.id.asc()
        )
        .all()
    )

    return {
        "decision_id": decision.id,
        "decision_title": decision.title,
        "alternatives_count": len(alternatives),
        "alternatives": [
            {
                "id": alternative.id,
                "name": alternative.name,
                "description": alternative.description,
                "pros": alternative.pros,
                "cons": alternative.cons,
                "estimated_cost": alternative.estimated_cost,
                "feasibility_score": alternative.feasibility_score,
                "risk_level": alternative.risk_level
            }
            for alternative in alternatives
        ]
    }


# =========================================================
# ASSIGN TAGS TO DECISION
# =========================================================

@router.post(
    "/{decision_id}/tags",
    response_model=list[TagResponse]
)
def assign_tags_to_decision(
    decision_id: int,
    tag_data: AssignTagsRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
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

    requested_tag_ids = set(tag_data.tag_ids)

    if not requested_tag_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tag_ids cannot be empty"
        )

    tags = (
        db.query(Tag)
        .filter(Tag.id.in_(requested_tag_ids))
        .all()
    )

    found_tag_ids = {
        tag.id
        for tag in tags
    }

    invalid_tag_ids = requested_tag_ids - found_tag_ids

    if invalid_tag_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid tag IDs: {sorted(invalid_tag_ids)}"
        )

    existing_tag_ids = {
        tag.id
        for tag in decision.tags
    }

    for tag in tags:
        if tag.id not in existing_tag_ids:
            decision.tags.append(tag)

    db.commit()
    db.refresh(decision)

    return decision.tags


# =========================================================
# GET DECISION TAGS
# =========================================================

@router.get(
    "/{decision_id}/tags",
    response_model=list[TagResponse]
)
def get_decision_tags(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
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

    return decision.tags


# =========================================================
# REMOVE TAG FROM DECISION
# =========================================================

@router.delete(
    "/{decision_id}/tags/{tag_id}"
)
def remove_tag_from_decision(
    decision_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
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

    tag = (
        db.query(Tag)
        .filter(Tag.id == tag_id)
        .first()
    )

    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    if tag not in decision.tags:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag is not associated with this decision"
        )

    decision.tags.remove(tag)

    db.commit()

    return {
        "message": "Tag removed from decision successfully"
    }


# =========================================================
# DECISION TIMELINE
# =========================================================

@router.get(
    "/{decision_id}/timeline"
)
def get_decision_timeline(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
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

    timeline = [
        {
            "event": "Decision Created",
            "decision_id": decision.id,
            "title": decision.title,
            "status": decision.status,
            "timestamp": decision.created_at
        }
    ]

    if decision.updated_at and decision.updated_at != decision.created_at:
        timeline.append(
            {
                "event": "Decision Updated",
                "decision_id": decision.id,
                "title": decision.title,
                "status": decision.status,
                "timestamp": decision.updated_at
            }
        )

    timeline.sort(
        key=lambda item: item["timestamp"]
    )

    return {
        "decision_id": decision.id,
        "timeline": timeline
    }


# =========================================================
# GET DECISION VERSIONS
# =========================================================

@router.get("/{decision_id}/versions")
def get_decision_versions(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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

    return versions


# =========================================================
# GET SPECIFIC DECISION VERSION
# =========================================================

@router.get("/{decision_id}/versions/{version_number}")
def get_specific_decision_version(
    decision_id: int,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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

    return version


# =========================================================
# DECISION CHANGE HISTORY
# =========================================================

@router.get("/{decision_id}/history")
def get_decision_history(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
        db.query(AuditLog)
        .filter(
            AuditLog.entity_type == "Decision",
            AuditLog.entity_id == decision_id
        )
        .order_by(
            AuditLog.created_at.asc()
        )
        .all()
    )

    return history


# =========================================================
# GET DECISION BY ID
# =========================================================

@router.get(
    "/{decision_id}",
    response_model=DecisionResponse
)
def get_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
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

    return decision


# =========================================================
# UPDATE DECISION
# =========================================================

@router.put(
    "/{decision_id}",
    response_model=DecisionResponse
)
def update_decision(
    decision_id: int,
    decision_data: DecisionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
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

    old_value = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category
    }

    decision.title = decision_data.title
    decision.problem_statement = decision_data.problem_statement
    decision.category = decision_data.category

    db.commit()
    db.refresh(decision)

    latest_version = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision.id
        )
        .order_by(
            DecisionVersion.version_number.desc()
        )
        .first()
    )

    next_version_number = (
        latest_version.version_number + 1
        if latest_version
        else 1
    )

    new_version = DecisionVersion(
        decision_id=decision.id,
        version_number=next_version_number,
        title=decision.title,
        problem_statement=decision.problem_statement,
        description=None,
        category=decision.category,
        status=decision.status,
        created_by=current_user.id
    )

    db.add(new_version)
    db.commit()
    db.refresh(new_version)

    create_activity_log(
        db=db,
        user=current_user,
        action="UPDATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"Updated decision: {decision.title}"
    )

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"Updated decision: {decision.title}",
        old_value=old_value,
        new_value={
            "title": decision.title,
            "problem_statement": decision.problem_statement,
            "category": decision.category
        }
    )

    return decision


# =========================================================
# UPDATE DECISION STATUS
# =========================================================

@router.put(
    "/{decision_id}/status",
    response_model=DecisionResponse,
    status_code=status.HTTP_200_OK
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

    old_status = decision.status
    new_status = status_data.status.value

    # -----------------------------------------------------
    # VALID STATUS TRANSITIONS
    # -----------------------------------------------------

    valid_transitions = {
        "Draft": ["Draft", "Under Review"],
        "Under Review": [
            "Under Review",
            "Approved",
            "Rejected"
        ],
        "Approved": [
            "Approved",
            "Archived"
        ],
        "Rejected": [
            "Rejected",
            "Draft"
        ],
        "Archived": [
            "Archived"
        ]
    }

    allowed_statuses = valid_transitions.get(
        old_status,
        []
    )

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid status transition: "
                f"{old_status} -> {new_status}. "
                f"Allowed transitions from {old_status}: "
                f"{', '.join(allowed_statuses)}"
            )
        )

    # No actual change
    if old_status == new_status:
        return decision

    decision.status = new_status

    db.commit()
    db.refresh(decision)

    latest_version = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision.id
        )
        .order_by(
            DecisionVersion.version_number.desc()
        )
        .first()
    )

    next_version_number = (
        latest_version.version_number + 1
        if latest_version
        else 1
    )

    new_version = DecisionVersion(
        decision_id=decision.id,
        version_number=next_version_number,
        title=decision.title,
        problem_statement=decision.problem_statement,
        description=None,
        category=decision.category,
        status=decision.status,
        created_by=current_user.id
    )

    db.add(new_version)
    db.commit()
    db.refresh(new_version)

    if new_status == "Under Review" and old_status == "Draft":

        audit_action = "SUBMIT"
        activity_action = "SUBMIT"

        description = (
            f"Submitted decision for review "
            f"by changing status from {old_status} to {new_status}"
        )

    elif new_status == "Archived":

        audit_action = "ARCHIVE"
        activity_action = "ARCHIVE"

        description = (
            f"Archived decision "
            f"by changing status from {old_status} to {new_status}"
        )

    else:

        audit_action = "UPDATE"
        activity_action = "STATUS_CHANGE"

        description = (
            f"Changed decision status "
            f"from {old_status} to {new_status}"
        )

    create_activity_log(
        db=db,
        user=current_user,
        action=activity_action,
        entity_type="Decision",
        entity_id=decision.id,
        description=description
    )

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action=audit_action,
        entity_type="Decision",
        entity_id=decision.id,
        description=description,
        old_value={
            "status": old_status
        },
        new_value={
            "status": new_status
        }
    )

    return decision


# =========================================================
# UPDATE DECISION RATIONALE
# =========================================================

@router.put(
    "/{decision_id}/rationale",
    response_model=DecisionResponse
)
def update_decision_rationale(
    decision_id: int,
    rationale_data: DecisionRationaleUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
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

    old_rationale = decision.rationale

    decision.rationale = rationale_data.rationale

    db.commit()
    db.refresh(decision)

    latest_version = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision.id
        )
        .order_by(
            DecisionVersion.version_number.desc()
        )
        .first()
    )

    next_version_number = (
        latest_version.version_number + 1
        if latest_version
        else 1
    )

    new_version = DecisionVersion(
        decision_id=decision.id,
        version_number=next_version_number,
        title=decision.title,
        problem_statement=decision.problem_statement,
        description=None,
        category=decision.category,
        status=decision.status,
        created_by=current_user.id
    )

    db.add(new_version)
    db.commit()
    db.refresh(new_version)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"Updated rationale for decision: {decision.title}",
        old_value={
            "rationale": old_rationale
        },
        new_value={
            "rationale": decision.rationale
        }
    )

    return decision


# =========================================================
# GET DECISION RATIONALE
# =========================================================

@router.get(
    "/{decision_id}/rationale"
)
def get_decision_rationale(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
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

    return {
        "decision_id": decision.id,
        "rationale": decision.rationale
    }


# =========================================================
# DELETE DECISION
# ADMIN ONLY
# =========================================================

@router.delete(
    "/{decision_id}",
    status_code=status.HTTP_200_OK
)
def delete_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
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

    old_value = {
        "id": decision.id,
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category,
        "status": decision.status,
        "rationale": decision.rationale
    }

    decision_id_value = decision.id
    decision_title = decision.title

    db.delete(decision)
    db.commit()

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="Decision",
        entity_id=decision_id_value,
        description=f"Deleted decision: {decision_title}",
        old_value=old_value,
        new_value=None
    )

    return {
        "message": "Decision deleted successfully"
    }