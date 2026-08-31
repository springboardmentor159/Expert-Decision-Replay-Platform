from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.models.decision import Decision
from app.models.tag import Tag
from app.models.decision_activity import DecisionActivity
from app.models.activity_log import ActivityLog
from app.models.audit_log import AuditLog
from app.models.decision_version import DecisionVersion
from app.models.access_log import AccessLog

from app.schemas.decision import (
    DecisionCreate,
    DecisionResponse,
    DecisionStatusUpdate,
    DecisionUpdate,
    RationaleUpdate,
)

from app.schemas.tag import DecisionTagAssign

from app.core.security import get_current_user


router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
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
    decision: DecisionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    user_id = int(current_user["sub"])

    # Create Decision
    new_decision = Decision(
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status="Draft",
        created_by=user_id
    )

    db.add(new_decision)
    db.commit()
    db.refresh(new_decision)

    # Audit Log
    audit = AuditLog(
        user_id=user_id,
        action="CREATE",
        entity_type="Decision",
        entity_id=new_decision.id,
        description=f"Decision {new_decision.id} created",
        new_value=new_decision.title
    )

    db.add(audit)

    # Decision Timeline Activity
    timeline_activity = DecisionActivity(
        decision_id=new_decision.id,
        activity_type="Created",
        description="Decision created",
        created_by=user_id
    )

    db.add(timeline_activity)

    # Activity Log
    log = ActivityLog(
        user_id=user_id,
        action="Decision Created",
        entity_type="Decision",
        entity_id=new_decision.id,
        description=f"Decision {new_decision.id} created"
    )

    db.add(log)

    db.commit()

    return new_decision


# =========================================================
# GET ALL / FILTERED / SEARCHED / SORTED DECISIONS
# =========================================================

@router.get(
    "",
    response_model=list[DecisionResponse]
)
def get_decisions(
    status: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    tag: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    query = db.query(Decision)

    # Filter by Status
    if status:
        query = query.filter(
            Decision.status == status
        )

    # Filter by Category
    if category:
        query = query.filter(
            Decision.category == category
        )

    # Search
    if search:

        search_pattern = f"%{search}%"

        query = query.filter(
            (Decision.title.ilike(search_pattern)) |
            (Decision.problem_statement.ilike(search_pattern))
        )

    # Filter by Tag
    if tag:

        query = query.join(
            Decision.tags
        ).filter(
            Tag.name == tag
        )

    # Pagination Validation
    if page < 1:

        raise HTTPException(
            status_code=400,
            detail="Page must be greater than or equal to 1"
        )

    if limit < 1 or limit > 100:

        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100"
        )

    # Allowed Sorting Fields
    allowed_sort_fields = {

        "created_at": Decision.created_at,
        "updated_at": Decision.updated_at,
        "title": Decision.title,
        "status": Decision.status,
        "category": Decision.category

    }

    if sort_by not in allowed_sort_fields:

        raise HTTPException(
            status_code=400,
            detail="Invalid sort field"
        )

    sort_column = allowed_sort_fields[sort_by]

    # Sorting
    if sort_order.lower() == "asc":

        query = query.order_by(
            sort_column.asc()
        )

    elif sort_order.lower() == "desc":

        query = query.order_by(
            sort_column.desc()
        )

    else:

        raise HTTPException(
            status_code=400,
            detail="sort_order must be 'asc' or 'desc'"
        )

    # Pagination
    offset = (page - 1) * limit

    return (
        query
        .distinct()
        .offset(offset)
        .limit(limit)
        .all()
    )


# =========================================================
# ASSIGN TAGS TO DECISION
# =========================================================

@router.post(
    "/{decision_id}/tags"
)
def assign_tags(
    decision_id: int,
    data: DecisionTagAssign,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    user_id = int(current_user["sub"])

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

    tags = (
        db.query(Tag)
        .filter(Tag.id.in_(data.tag_ids))
        .all()
    )

    if len(tags) != len(set(data.tag_ids)):

        raise HTTPException(
            status_code=404,
            detail="One or more tags not found"
        )

    added_tags = []

    for tag in tags:

        if tag not in decision.tags:

            decision.tags.append(tag)
            added_tags.append(tag)

    # Timeline + Activity Logs
    for tag in added_tags:

        timeline_activity = DecisionActivity(
            decision_id=decision.id,
            activity_type="Tag Added",
            description=f"Tag '{tag.name}' added to decision",
            created_by=user_id
        )

        db.add(timeline_activity)

        log = ActivityLog(
            user_id=user_id,
            action="Tag Added",
            entity_type="Decision",
            entity_id=decision.id,
            description=f"Tag '{tag.name}' added to decision {decision.id}"
        )

        db.add(log)

    db.commit()

    return {
        "message": "Tags assigned successfully",
        "decision_id": decision_id,
        "tags": [
            {
                "id": tag.id,
                "name": tag.name
            }
            for tag in decision.tags
        ]
    }


# =========================================================
# GET TAGS FOR A DECISION
# =========================================================

@router.get(
    "/{decision_id}/tags"
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
            status_code=404,
            detail="Decision not found"
        )

    return [
        {
            "id": tag.id,
            "name": tag.name
        }
        for tag in decision.tags
    ]


# =========================================================
# REMOVE TAG FROM DECISION
# =========================================================

@router.delete(
    "/{decision_id}/tags/{tag_id}"
)
def remove_tag(
    decision_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    user_id = int(current_user["sub"])

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

    tag = (
        db.query(Tag)
        .filter(Tag.id == tag_id)
        .first()
    )

    if tag is None:

        raise HTTPException(
            status_code=404,
            detail="Tag not found"
        )

    if tag not in decision.tags:

        raise HTTPException(
            status_code=404,
            detail="Tag is not assigned to this decision"
        )

    tag_name = tag.name

    decision.tags.remove(tag)

    # Timeline Activity
    timeline_activity = DecisionActivity(
        decision_id=decision.id,
        activity_type="Tag Removed",
        description=f"Tag '{tag_name}' removed from decision",
        created_by=user_id
    )

    db.add(timeline_activity)

    # Activity Log
    log = ActivityLog(
        user_id=user_id,
        action="Tag Removed",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"Tag '{tag_name}' removed from decision {decision.id}"
    )

    db.add(log)

    db.commit()

    return {
        "message": "Tag removed from decision successfully"
    }


# =========================================================
# GET DECISION TIMELINE
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
            status_code=404,
            detail="Decision not found"
        )

    activities = (
        db.query(DecisionActivity)
        .filter(
            DecisionActivity.decision_id == decision_id
        )
        .order_by(
            DecisionActivity.created_at.asc()
        )
        .all()
    )

    return {
        "decision_id": decision_id,
        "timeline": [
            {
                "id": activity.id,
                "activity_type": activity.activity_type,
                "description": activity.description,
                "created_by": activity.created_by,
                "created_at": activity.created_at
            }
            for activity in activities
        ]
    }


# =========================================================
# GET DECISION HISTORY
# =========================================================

@router.get(
    "/{decision_id}/history"
)
def get_decision_history(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # IMPORTANT:
    # First check whether the Decision exists.
    # This prevents a non-existing decision from
    # incorrectly returning 200 with an empty history.

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

    return {
        "decision_id": decision_id,
        "history": [
            {
                "id": version.id,
                "decision_id": version.decision_id,
                "version_number": version.version_number,
                "title": version.title,
                "problem_statement": version.problem_statement,
                "category": version.category,
                "rationale": version.rationale,
                "status": version.status,
                "created_by": version.created_by,
                "created_at": version.created_at
            }
            for version in versions
        ]
    }


# =========================================================
# GET ALL DECISION VERSIONS
# =========================================================

@router.get(
    "/{decision_id}/versions"
)
def get_decision_versions(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # IMPORTANT:
    # Check the Decision first.
    # Non-existing Decision must return 404.

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

    return {
        "decision_id": decision_id,
        "versions": [
            {
                "id": version.id,
                "decision_id": version.decision_id,
                "version_number": version.version_number,
                "title": version.title,
                "problem_statement": version.problem_statement,
                "category": version.category,
                "rationale": version.rationale,
                "status": version.status,
                "created_by": version.created_by,
                "created_at": version.created_at
            }
            for version in versions
        ]
    }


# =========================================================
# GET SPECIFIC DECISION VERSION
# =========================================================

@router.get(
    "/{decision_id}/versions/{version_number}"
)
def get_specific_decision_version(
    decision_id: int,
    version_number: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # First check Decision
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

    # Then find requested version
    version = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision_id,
            DecisionVersion.version_number == version_number
        )
        .first()
    )

    if version is None:

        raise HTTPException(
            status_code=404,
            detail="Decision version not found"
        )

    return {
        "id": version.id,
        "decision_id": version.decision_id,
        "version_number": version.version_number,
        "title": version.title,
        "problem_statement": version.problem_statement,
        "category": version.category,
        "rationale": version.rationale,
        "status": version.status,
        "created_by": version.created_by,
        "created_at": version.created_at
    }


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

    user_id = int(current_user["sub"])

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

    # =====================================================
    # SPRINT 11 - ACCESS LOG
    # =====================================================

    access_log = AccessLog(
        user_id=user_id,
        resource_type="Decision",
        resource_id=decision.id,
        action="VIEW",
        ip_address=None
    )

    db.add(access_log)
    db.commit()

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

    user_id = int(current_user["sub"])

    # Find Decision
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

    # =====================================================
    # CREATE VERSION BEFORE UPDATE
    # =====================================================

    last_version = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision.id
        )
        .order_by(
            DecisionVersion.version_number.desc()
        )
        .first()
    )

    if last_version:
        next_version_number = (
            last_version.version_number + 1
        )
    else:
        next_version_number = 1

    version = DecisionVersion(
        decision_id=decision.id,
        version_number=next_version_number,
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        rationale=decision.rationale,
        status=decision.status,
        created_by=user_id
    )

    db.add(version)

    # =====================================================
    # UPDATE DECISION
    # =====================================================

    old_title = decision.title

    decision.title = decision_data.title
    decision.problem_statement = decision_data.problem_statement
    decision.category = decision_data.category

    db.commit()
    db.refresh(decision)

    # =====================================================
    # DECISION TIMELINE
    # =====================================================

    timeline_activity = DecisionActivity(
        decision_id=decision.id,
        activity_type="Decision Updated",
        description=(
            f"Decision updated and version "
            f"{next_version_number} created"
        ),
        created_by=user_id
    )

    db.add(timeline_activity)

    # =====================================================
    # ACTIVITY LOG
    # =====================================================

    log = ActivityLog(
        user_id=user_id,
        action="Decision Updated",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"Decision {decision.id} updated; "
            f"version {next_version_number} created"
        )
    )

    db.add(log)

    # =====================================================
    # AUDIT LOG
    # =====================================================

    audit = AuditLog(
        user_id=user_id,
        action="UPDATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"Decision {decision.id} updated; "
            f"version {next_version_number} created"
        ),
        old_value=old_title,
        new_value=decision.title
    )

    db.add(audit)

    db.commit()

    return decision


# =========================================================
# UPDATE STATUS
# =========================================================

@router.patch(
    "/{decision_id}/status",
    response_model=DecisionResponse
)
def update_decision_status(
    decision_id: int,
    status_data: DecisionStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    user_id = int(current_user["sub"])

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

    old_status = decision.status
    new_status = status_data.status.value

    decision.status = new_status

    db.commit()
    db.refresh(decision)

    # Timeline Activity
    timeline_activity = DecisionActivity(
        decision_id=decision.id,
        activity_type="Status Changed",
        description=(
            f"Status changed from "
            f"{old_status} to {new_status}"
        ),
        created_by=user_id
    )

    db.add(timeline_activity)

    # Activity Log
    log = ActivityLog(
        user_id=user_id,
        action="Decision Status Changed",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"Decision {decision.id} status changed "
            f"from {old_status} to {new_status}"
        )
    )

    db.add(log)

    db.commit()

    return decision


# =========================================================
# UPDATE DECISION RATIONALE
# =========================================================

@router.put(
    "/{decision_id}/rationale"
)
def update_decision_rationale(
    decision_id: int,
    rationale_data: RationaleUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    user_id = int(current_user["sub"])

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

    decision.rationale = rationale_data.rationale

    db.commit()
    db.refresh(decision)

    # Timeline Activity
    timeline_activity = DecisionActivity(
        decision_id=decision.id,
        activity_type="Rationale Updated",
        description="Decision rationale updated",
        created_by=user_id
    )

    db.add(timeline_activity)

    # Activity Log
    log = ActivityLog(
        user_id=user_id,
        action="Rationale Updated",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"Rationale updated for decision {decision.id}"
    )

    db.add(log)

    db.commit()

    return {
        "message": "Decision rationale updated successfully",
        "decision_id": decision.id,
        "rationale": decision.rationale
    }