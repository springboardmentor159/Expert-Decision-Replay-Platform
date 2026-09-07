from typing import Optional, List
from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
    Path,
)

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, or_

from app.db.database import get_db

from app.models.decision import Decision
from app.models.decision_version import DecisionVersion
from app.models.audit_log import AuditLog
from app.models.tag import Tag
from app.models.user import User
from app.models.alternative import Alternative
from app.models.comment import Comment
from app.models.discussion_thread import DiscussionThread

from app.core.security import get_current_user
from app.core.enums import DecisionStatus

from app.services.activity import log_activity
from app.services.audit import log_audit
from app.services.access import log_access


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)


# =========================================================
# PYDANTIC MODELS
# =========================================================

class DecisionCreate(BaseModel):
    title: str = Field(..., min_length=1)
    problem_statement: str = Field(..., min_length=1)
    rationale: Optional[str] = None
    category: str = Field(..., min_length=1)


class DecisionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    problem_statement: Optional[str] = Field(None, min_length=1)
    rationale: Optional[str] = None
    category: Optional[str] = Field(None, min_length=1)
    status: Optional[DecisionStatus] = None


class AssignTagsRequest(BaseModel):
    tag_ids: List[int]


class DecisionResponse(BaseModel):
    id: int
    title: str
    problem_statement: str
    rationale: Optional[str]
    category: str
    status: DecisionStatus
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =========================================================
# HELPERS
# =========================================================

def get_decision_or_404(
    decision_id: int,
    db: Session
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return decision


def decision_snapshot(decision: Decision):
    """
    Create a safe snapshot of the current decision state.

    This is used for audit old_value/new_value and
    decision version tracking.

    No passwords, JWTs, secrets, or credentials are stored.
    """

    return {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "rationale": decision.rationale,
        "category": decision.category,
        "status": (
            decision.status.value
            if hasattr(decision.status, "value")
            else str(decision.status)
        ),
    }


def version_snapshot(version: DecisionVersion):
    """
    Convert a DecisionVersion into a JSON-safe response.
    """

    return {
        "id": version.id,
        "decision_id": version.decision_id,
        "version_number": version.version_number,
        "title": version.title,
        "problem_statement": version.problem_statement,
        "rationale": version.rationale,
        "category": version.category,
        "status": (
            version.status.value
            if hasattr(version.status, "value")
            else str(version.status)
        ),
        "created_by": version.created_by,
        "created_at": version.created_at,
    }


def create_decision_version(
    db: Session,
    decision: Decision,
    user_id: int
):
    """
    Create the next sequential version.

    The client never supplies the version number.
    The backend determines it from the existing versions.
    """

    latest_version = db.query(
        DecisionVersion
    ).filter(
        DecisionVersion.decision_id == decision.id
    ).order_by(
        DecisionVersion.version_number.desc()
    ).first()

    if latest_version:
        next_version_number = (
            latest_version.version_number + 1
        )
    else:
        next_version_number = 1

    version = DecisionVersion(
        decision_id=decision.id,
        version_number=next_version_number,
        title=decision.title,
        problem_statement=decision.problem_statement,
        rationale=decision.rationale,
        category=decision.category,
        status=decision.status,
        created_by=user_id,
        created_at=datetime.utcnow()
    )

    db.add(version)

    return version


def normalize_timestamp(timestamp):
    """
    Normalize timestamps to UTC-aware values so that
    timezone-aware and timezone-naive timestamps can
    safely be compared and sorted.
    """

    if timestamp is None:
        return datetime.min.replace(
            tzinfo=timezone.utc
        )

    if timestamp.tzinfo is None:
        return timestamp.replace(
            tzinfo=timezone.utc
        )

    return timestamp.astimezone(
        timezone.utc
    )


# =========================================================
# CREATE DECISION
# =========================================================

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED
)
def create_decision(
    decision_data: DecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_decision = Decision(
        title=decision_data.title,
        problem_statement=decision_data.problem_statement,
        rationale=decision_data.rationale,
        category=decision_data.category,
        status=DecisionStatus.DRAFT,
        created_by=current_user.id
    )

    db.add(new_decision)

    db.flush()

    # -----------------------------------------------------
    # CREATE VERSION 1
    # -----------------------------------------------------

    version = create_decision_version(
        db=db,
        decision=new_decision,
        user_id=current_user.id
    )

    db.flush()

    # -----------------------------------------------------
    # ACTIVITY LOG
    # -----------------------------------------------------

    log_activity(
        db=db,
        user_id=current_user.id,
        action="Decision Created",
        entity_type="Decision",
        entity_id=new_decision.id,
        description=(
            f"User {current_user.id} created "
            f"Decision {new_decision.id}"
        )
    )

    # -----------------------------------------------------
    # AUDIT LOG
    # -----------------------------------------------------

    log_audit(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Decision",
        entity_id=new_decision.id,
        description=(
            f"Decision {new_decision.id} was created"
        ),
        old_value=None,
        new_value=decision_snapshot(new_decision),
        request_method="POST",
        endpoint="/decisions/"
    )

    db.commit()

    db.refresh(new_decision)
    db.refresh(version)

    return {
        "message": "Decision created successfully",
        "decision": {
            "id": new_decision.id,
            "title": new_decision.title,
            "problem_statement": new_decision.problem_statement,
            "rationale": new_decision.rationale,
            "category": new_decision.category,
            "status": new_decision.status,
            "created_by": new_decision.created_by,
            "created_at": new_decision.created_at,
            "updated_at": new_decision.updated_at
        },
        "version": {
            "version_number": version.version_number,
            "created_by": version.created_by,
            "created_at": version.created_at
        }
    }


# =========================================================
# SEARCH DECISIONS
# =========================================================

@router.get("/search")
def search_decisions(

    q: Optional[str] = Query(
        None,
        min_length=1,
        description=(
            "Search decision title, problem statement, "
            "or rationale"
        )
    ),

    category: Optional[str] = Query(
        None,
        description="Filter by category"
    ),

    decision_status: Optional[DecisionStatus] = Query(
        None,
        description="Filter by decision status"
    ),

    tag: Optional[str] = Query(
        None,
        description="Filter by tag name"
    ),

    page: int = Query(
        1,
        ge=1
    ),

    page_size: int = Query(
        20,
        ge=1,
        le=100
    ),

    sort_by: str = Query(
        "created_at",
        pattern="^(created_at|updated_at|title)$"
    ),

    order: str = Query(
        "desc",
        pattern="^(asc|desc)$"
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):

    query = db.query(Decision)

    if q:
        search_value = f"%{q}%"

        query = query.filter(
            or_(
                Decision.title.ilike(search_value),
                Decision.problem_statement.ilike(search_value),
                Decision.rationale.ilike(search_value)
            )
        )

    if category:
        query = query.filter(
            Decision.category.ilike(
                f"%{category}%"
            )
        )

    if decision_status:
        query = query.filter(
            Decision.status == decision_status
        )

    if tag:
        query = query.join(
            Decision.tags
        ).filter(
            Tag.name.ilike(
                f"%{tag}%"
            )
        ).distinct()

    total = query.count()

    if sort_by == "title":
        sort_column = Decision.title

    elif sort_by == "updated_at":
        sort_column = Decision.updated_at

    else:
        sort_column = Decision.created_at

    if order == "asc":
        query = query.order_by(
            asc(sort_column)
        )
    else:
        query = query.order_by(
            desc(sort_column)
        )

    offset = (page - 1) * page_size

    decisions = query.offset(
        offset
    ).limit(
        page_size
    ).all()

    results = []

    for decision in decisions:

        results.append({
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
        })

    return {
        "results": results,
        "page": page,
        "page_size": page_size,
        "total": total
    }


# =========================================================
# GET ALL DECISIONS
# =========================================================

@router.get("/")
def get_all_decisions(

    search: Optional[str] = Query(None),

    category: Optional[str] = Query(None),

    decision_status: Optional[DecisionStatus] = Query(None),

    tag: Optional[str] = Query(None),

    page: int = Query(
        1,
        ge=1
    ),

    page_size: int = Query(
        20,
        ge=1,
        le=100
    ),

    sort_by: str = Query(
        "created_at",
        pattern="^(created_at|updated_at|title)$"
    ),

    order: str = Query(
        "desc",
        pattern="^(asc|desc)$"
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):

    query = db.query(Decision)

    if search:

        search_value = f"%{search}%"

        query = query.filter(
            or_(
                Decision.title.ilike(search_value),
                Decision.problem_statement.ilike(search_value),
                Decision.rationale.ilike(search_value)
            )
        )

    if category:

        query = query.filter(
            Decision.category.ilike(
                f"%{category}%"
            )
        )

    if decision_status:

        query = query.filter(
            Decision.status == decision_status
        )

    if tag:

        query = query.join(
            Decision.tags
        ).filter(
            Tag.name.ilike(
                f"%{tag}%"
            )
        ).distinct()

    total = query.count()

    if sort_by == "title":
        sort_column = Decision.title

    elif sort_by == "updated_at":
        sort_column = Decision.updated_at

    else:
        sort_column = Decision.created_at

    if order == "asc":
        query = query.order_by(
            asc(sort_column)
        )
    else:
        query = query.order_by(
            desc(sort_column)
        )

    offset = (page - 1) * page_size

    decisions = query.offset(
        offset
    ).limit(
        page_size
    ).all()

    return {
        "items": decisions,
        "page": page,
        "page_size": page_size,
        "total": total,
        "count": len(decisions)
    }


# =========================================================
# GET DECISION BY ID
# =========================================================

@router.get("/{decision_id}")
def get_decision(

    decision_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):

    decision = get_decision_or_404(
        decision_id,
        db
    )

    # -----------------------------------------------------
    # AUDIT LOG
    # -----------------------------------------------------

    log_audit(
        db=db,
        user_id=current_user.id,
        action="ACCESS",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"User {current_user.id} accessed "
            f"Decision {decision.id}"
        ),
        request_method="GET",
        endpoint=f"/decisions/{decision.id}"
    )

    # -----------------------------------------------------
    # ACCESS LOG
    # -----------------------------------------------------

    log_access(
        db=db,
        user_id=current_user.id,
        resource_type="Decision",
        resource_id=decision.id,
        action="VIEW"
    )

    db.commit()

    return decision


# =========================================================
# UPDATE DECISION
# =========================================================

@router.put("/{decision_id}")
def update_decision(

    decision_id: int,

    decision_data: DecisionUpdate,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):

    decision = get_decision_or_404(
        decision_id,
        db
    )

    old_state = decision_snapshot(decision)

    old_status = decision.status

    update_data = decision_data.model_dump(
        exclude_unset=True
    )

    if not update_data:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    for field, value in update_data.items():

        setattr(
            decision,
            field,
            value
        )

    db.flush()

    new_state = decision_snapshot(decision)

    version = create_decision_version(
        db=db,
        decision=decision,
        user_id=current_user.id
    )

    db.flush()

    if (
        "status" in update_data
        and old_status != decision.status
    ):

        if decision.status == DecisionStatus.APPROVED:
            audit_action = "APPROVE"

        elif decision.status == DecisionStatus.REJECTED:
            audit_action = "REJECT"

        elif decision.status == DecisionStatus.UNDER_REVIEW:
            audit_action = "SUBMIT"

        else:
            audit_action = "UPDATE"

    else:
        audit_action = "UPDATE"

    log_audit(
        db=db,
        user_id=current_user.id,
        action=audit_action,
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"User {current_user.id} updated "
            f"Decision {decision.id}"
        ),
        old_value=old_state,
        new_value=new_state,
        request_method="PUT",
        endpoint=f"/decisions/{decision.id}"
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="Decision Updated",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"User {current_user.id} updated "
            f"Decision {decision.id}"
        )
    )

    if (
        "status" in update_data
        and old_status != decision.status
    ):

        log_activity(
            db=db,
            user_id=current_user.id,
            action="Decision Status Changed",
            entity_type="Decision",
            entity_id=decision.id,
            description=(
                f"Decision {decision.id} status changed "
                f"from '{old_status.value}' to "
                f"'{decision.status.value}'"
            )
        )

    db.commit()

    db.refresh(decision)
    db.refresh(version)

    return {
        "message": "Decision updated successfully",
        "decision": {
            "id": decision.id,
            "title": decision.title,
            "problem_statement": decision.problem_statement,
            "rationale": decision.rationale,
            "category": decision.category,
            "status": decision.status,
            "created_by": decision.created_by,
            "created_at": decision.created_at,
            "updated_at": decision.updated_at
        },
        "version": {
            "id": version.id,
            "version_number": version.version_number,
            "created_by": version.created_by,
            "created_at": version.created_at
        },
        "changes": {
            "old_value": old_state,
            "new_value": new_state
        }
    }


# =========================================================
# DELETE DECISION
# =========================================================

@router.delete("/{decision_id}")
def delete_decision(

    decision_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):

    decision = get_decision_or_404(
        decision_id,
        db
    )

    old_state = decision_snapshot(decision)

    decision_title = decision.title

    log_audit(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"User {current_user.id} deleted "
            f"Decision {decision.id}"
        ),
        old_value=old_state,
        new_value=None,
        request_method="DELETE",
        endpoint=f"/decisions/{decision.id}"
    )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="Decision Deleted",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"User {current_user.id} deleted "
            f"Decision {decision.id} "
            f"('{decision_title}')"
        )
    )

    db.delete(decision)

    db.commit()

    return {
        "message": "Decision deleted successfully"
    }


# =========================================================
# COMPARE DECISION ALTERNATIVES
# =========================================================

@router.get("/{decision_id}/alternatives/compare")
def compare_decision_alternatives(

    decision_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):

    decision = get_decision_or_404(
        decision_id,
        db
    )

    alternatives = db.query(
        Alternative
    ).filter(
        Alternative.decision_id == decision.id
    ).order_by(
        Alternative.id.asc()
    ).all()

    # -----------------------------------------------------
    # AUDIT LOG
    # -----------------------------------------------------

    log_audit(
        db=db,
        user_id=current_user.id,
        action="ACCESS",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"User {current_user.id} compared "
            f"alternatives for Decision {decision.id}"
        ),
        request_method="GET",
        endpoint=(
            f"/decisions/{decision.id}/"
            f"alternatives/compare"
        )
    )

    # -----------------------------------------------------
    # ACCESS LOG
    # -----------------------------------------------------

    log_access(
        db=db,
        user_id=current_user.id,
        resource_type="Decision",
        resource_id=decision.id,
        action="VIEW"
    )

    db.commit()

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {
        "decision_id": decision.id,
        "decision_title": decision.title,
        "alternative_count": len(alternatives),
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
# DECISION VERSIONS
# =========================================================

@router.get("/{decision_id}/versions")
def get_decision_versions(

    decision_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):

    decision = get_decision_or_404(
        decision_id,
        db
    )

    versions = db.query(
        DecisionVersion
    ).filter(
        DecisionVersion.decision_id == decision.id
    ).order_by(
        DecisionVersion.version_number.asc()
    ).all()

    # -----------------------------------------------------
    # AUDIT LOG
    # -----------------------------------------------------

    log_audit(
        db=db,
        user_id=current_user.id,
        action="ACCESS",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"User {current_user.id} accessed "
            f"version history of Decision {decision.id}"
        ),
        request_method="GET",
        endpoint=f"/decisions/{decision.id}/versions"
    )

    # -----------------------------------------------------
    # ACCESS LOG
    # -----------------------------------------------------

    log_access(
        db=db,
        user_id=current_user.id,
        resource_type="Decision",
        resource_id=decision.id,
        action="VIEW"
    )

    db.commit()

    return {
        "decision_id": decision.id,
        "count": len(versions),
        "versions": [
            version_snapshot(version)
            for version in versions
        ]
    }


# =========================================================
# GET SPECIFIC VERSION
# =========================================================

@router.get(
    "/{decision_id}/versions/{version_number}"
)
def get_specific_decision_version(

    decision_id: int,

    version_number: int = Path(
        ...,
        ge=1,
        description="Version number must be 1 or greater"
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):

    decision = get_decision_or_404(
        decision_id,
        db
    )

    version = db.query(
        DecisionVersion
    ).filter(
        DecisionVersion.decision_id == decision.id,
        DecisionVersion.version_number == version_number
    ).first()

    if not version:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Version {version_number} "
                f"not found for Decision {decision_id}"
            )
        )

    log_audit(
        db=db,
        user_id=current_user.id,
        action="ACCESS",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"User {current_user.id} accessed "
            f"Decision {decision.id} "
            f"Version {version_number}"
        ),
        request_method="GET",
        endpoint=(
            f"/decisions/{decision.id}/"
            f"versions/{version_number}"
        )
    )

    # -----------------------------------------------------
    # ACCESS LOG
    # -----------------------------------------------------

    log_access(
        db=db,
        user_id=current_user.id,
        resource_type="DecisionVersion",
        resource_id=version.id,
        action="VIEW"
    )

    db.commit()

    return version_snapshot(version)


# =========================================================
# DECISION HISTORY
# =========================================================

@router.get("/{decision_id}/history")
def get_decision_history(

    decision_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):

    decision = get_decision_or_404(
        decision_id,
        db
    )

    history = []

    audit_logs = db.query(
        AuditLog
    ).filter(
        AuditLog.entity_type == "Decision",
        AuditLog.entity_id == decision.id
    ).order_by(
        AuditLog.created_at.asc(),
        AuditLog.id.asc()
    ).all()

    for audit in audit_logs:

        history.append({
            "id": audit.id,
            "source": "audit_log",
            "action": audit.action,
            "entity_type": audit.entity_type,
            "entity_id": audit.entity_id,
            "description": audit.description,
            "user_id": audit.user_id,
            "old_value": audit.old_value,
            "new_value": audit.new_value,
            "created_at": audit.created_at
        })

    if not audit_logs:

        history.append({
            "id": None,
            "source": "decision",
            "action": "CREATE",
            "entity_type": "Decision",
            "entity_id": decision.id,
            "description": (
                f"Decision '{decision.title}' "
                f"was created"
            ),
            "user_id": decision.created_by,
            "old_value": None,
            "new_value": decision_snapshot(decision),
            "created_at": decision.created_at
        })

    # -----------------------------------------------------
    # ACCESS AUDIT
    #
    # Log after retrieving history so that this request
    # does not appear inside its own response.
    # -----------------------------------------------------

    log_audit(
        db=db,
        user_id=current_user.id,
        action="ACCESS",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"User {current_user.id} accessed "
            f"history of Decision {decision.id}"
        ),
        request_method="GET",
        endpoint=f"/decisions/{decision.id}/history"
    )

    # -----------------------------------------------------
    # ACCESS LOG
    # -----------------------------------------------------

    log_access(
        db=db,
        user_id=current_user.id,
        resource_type="Decision",
        resource_id=decision.id,
        action="VIEW"
    )

    db.commit()

    history.sort(
        key=lambda item: (
            normalize_timestamp(
                item["created_at"]
            ),
            item["id"] if item["id"] is not None else 0
        )
    )

    return {
        "decision_id": decision.id,
        "count": len(history),
        "history": history
    }


# =========================================================
# ASSIGN TAGS
# =========================================================

@router.post("/{decision_id}/tags")
def assign_tags_to_decision(

    decision_id: int,

    tag_data: AssignTagsRequest,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):

    decision = get_decision_or_404(
        decision_id,
        db
    )

    requested_tag_ids = set(
        tag_data.tag_ids
    )

    if not requested_tag_ids:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one tag ID is required"
        )

    tags = db.query(Tag).filter(
        Tag.id.in_(requested_tag_ids)
    ).all()

    found_tag_ids = {
        tag.id
        for tag in tags
    }

    missing_tag_ids = (
        requested_tag_ids - found_tag_ids
    )

    if missing_tag_ids:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Tags not found: "
                f"{list(missing_tag_ids)}"
            )
        )

    newly_assigned = []

    for tag in tags:

        if tag not in decision.tags:

            decision.tags.append(tag)
            newly_assigned.append(tag)

    db.flush()

    if newly_assigned:

        tag_names = ", ".join(
            tag.name
            for tag in newly_assigned
        )

        log_activity(
            db=db,
            user_id=current_user.id,
            action="Tags Assigned",
            entity_type="Decision",
            entity_id=decision.id,
            description=(
                f"User {current_user.id} assigned "
                f"tags [{tag_names}] to "
                f"Decision {decision.id}"
            )
        )

        log_audit(
            db=db,
            user_id=current_user.id,
            action="UPDATE",
            entity_type="Decision",
            entity_id=decision.id,
            description=(
                f"Tags assigned to Decision {decision.id}"
            ),
            new_value={
                "tags_added": [
                    {
                        "id": tag.id,
                        "name": tag.name
                    }
                    for tag in newly_assigned
                ]
            },
            request_method="POST",
            endpoint=f"/decisions/{decision.id}/tags"
        )

    db.commit()

    db.refresh(decision)

    return {
        "message": "Tags assigned successfully",
        "decision_id": decision.id,
        "tags": [
            {
                "id": tag.id,
                "name": tag.name
            }
            for tag in decision.tags
        ]
    }


# =========================================================
# GET DECISION TAGS
# =========================================================

@router.get("/{decision_id}/tags")
def get_decision_tags(

    decision_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):

    decision = get_decision_or_404(
        decision_id,
        db
    )

    # -----------------------------------------------------
    # ACCESS AUDIT
    # -----------------------------------------------------

    log_audit(
        db=db,
        user_id=current_user.id,
        action="ACCESS",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"User {current_user.id} accessed "
            f"tags of Decision {decision.id}"
        ),
        request_method="GET",
        endpoint=f"/decisions/{decision.id}/tags"
    )

    # -----------------------------------------------------
    # ACCESS LOG
    # -----------------------------------------------------

    log_access(
        db=db,
        user_id=current_user.id,
        resource_type="Decision",
        resource_id=decision.id,
        action="VIEW"
    )

    db.commit()

    return {
        "decision_id": decision.id,
        "tags": [
            {
                "id": tag.id,
                "name": tag.name,
                "created_at": tag.created_at
            }
            for tag in decision.tags
        ]
    }


# =========================================================
# REMOVE TAG
# =========================================================

@router.delete(
    "/{decision_id}/tags/{tag_id}"
)
def remove_tag_from_decision(

    decision_id: int,

    tag_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):

    decision = get_decision_or_404(
        decision_id,
        db
    )

    tag = db.query(Tag).filter(
        Tag.id == tag_id
    ).first()

    if not tag:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    if tag not in decision.tags:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "This tag is not assigned "
                "to this decision"
            )
        )

    tag_name = tag.name

    decision.tags.remove(tag)

    db.flush()

    log_activity(
        db=db,
        user_id=current_user.id,
        action="Tag Removed",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"User {current_user.id} removed "
            f"tag '{tag_name}' from "
            f"Decision {decision.id}"
        )
    )

    log_audit(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"Tag '{tag_name}' removed from "
            f"Decision {decision.id}"
        ),
        old_value={
            "tag": {
                "id": tag.id,
                "name": tag.name
            }
        },
        new_value=None,
        request_method="DELETE",
        endpoint=(
            f"/decisions/{decision.id}/"
            f"tags/{tag.id}"
        )
    )

    db.commit()

    return {
        "message": "Tag removed successfully",
        "decision_id": decision_id,
        "tag_id": tag_id
    }


# =========================================================
# DECISION TIMELINE
# =========================================================

@router.get("/{decision_id}/timeline")
def get_decision_timeline(

    decision_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):

    decision = get_decision_or_404(
        decision_id,
        db
    )

    timeline = []

    # -----------------------------------------------------
    # DECISION CREATED
    # -----------------------------------------------------

    timeline.append({
        "event_type": "Decision created",
        "description": (
            f"Decision '{decision.title}' "
            f"was created"
        ),
        "timestamp": decision.created_at
    })

    # -----------------------------------------------------
    # AUDIT HISTORY
    # -----------------------------------------------------

    audit_logs = db.query(
        AuditLog
    ).filter(
        AuditLog.entity_type == "Decision",
        AuditLog.entity_id == decision.id
    ).order_by(
        AuditLog.created_at.asc()
    ).all()

    for audit in audit_logs:

        if audit.action == "ACCESS":
            continue

        timeline.append({
            "event_type": f"Decision {audit.action.lower()}",
            "description": audit.description,
            "timestamp": audit.created_at
        })

    # -----------------------------------------------------
    # ALTERNATIVES
    # -----------------------------------------------------

    alternatives = db.query(
        Alternative
    ).filter(
        Alternative.decision_id == decision_id
    ).all()

    for alternative in alternatives:

        timeline.append({
            "event_type": "Alternative created",
            "description": (
                f"Alternative '{alternative.name}' "
                f"was added"
            ),
            "timestamp": alternative.created_at
        })

        if alternative.updated_at:

            if (
                normalize_timestamp(
                    alternative.updated_at
                )
                !=
                normalize_timestamp(
                    alternative.created_at
                )
            ):

                timeline.append({
                    "event_type": "Alternative updated",
                    "description": (
                        f"Alternative "
                        f"'{alternative.name}' "
                        f"was updated"
                    ),
                    "timestamp": alternative.updated_at
                })

    # -----------------------------------------------------
    # COMMENTS
    # -----------------------------------------------------

    comments = db.query(
        Comment
    ).filter(
        Comment.decision_id == decision_id
    ).all()

    for comment in comments:

        timeline.append({
            "event_type": "Comment added",
            "description": (
                "A comment was added "
                "to the decision"
            ),
            "timestamp": comment.created_at
        })

        if getattr(comment, "updated_at", None):

            if (
                normalize_timestamp(
                    comment.updated_at
                )
                !=
                normalize_timestamp(
                    comment.created_at
                )
            ):

                timeline.append({
                    "event_type": "Comment updated",
                    "description": (
                        "A comment was updated "
                        "on the decision"
                    ),
                    "timestamp": comment.updated_at
                })

    # -----------------------------------------------------
    # DISCUSSION THREADS
    # -----------------------------------------------------

    discussion_threads = db.query(
        DiscussionThread
    ).filter(
        DiscussionThread.decision_id == decision_id
    ).all()

    for thread in discussion_threads:

        timeline.append({
            "event_type": "Discussion thread created",
            "description": (
                f"Discussion thread "
                f"'{thread.title}' was created"
            ),
            "timestamp": thread.created_at
        })

        if getattr(thread, "updated_at", None):

            if (
                normalize_timestamp(
                    thread.updated_at
                )
                !=
                normalize_timestamp(
                    thread.created_at
                )
            ):

                timeline.append({
                    "event_type": "Discussion thread updated",
                    "description": (
                        f"Discussion thread "
                        f"'{thread.title}' was updated"
                    ),
                    "timestamp": thread.updated_at
                })

    # -----------------------------------------------------
    # ACCESS AUDIT
    # -----------------------------------------------------

    log_audit(
        db=db,
        user_id=current_user.id,
        action="ACCESS",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"User {current_user.id} accessed "
            f"timeline of Decision {decision.id}"
        ),
        request_method="GET",
        endpoint=f"/decisions/{decision.id}/timeline"
    )

    # -----------------------------------------------------
    # ACCESS LOG
    # -----------------------------------------------------

    log_access(
        db=db,
        user_id=current_user.id,
        resource_type="Decision",
        resource_id=decision.id,
        action="VIEW"
    )

    db.commit()

    # -----------------------------------------------------
    # SORT
    # -----------------------------------------------------

    timeline.sort(
        key=lambda event: normalize_timestamp(
            event["timestamp"]
        )
    )

    return {
        "decision_id": decision_id,
        "timeline": timeline
    }