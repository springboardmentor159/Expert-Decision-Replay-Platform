from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.decision import Decision
from app.models.decision_version import DecisionVersion
from app.models.user import User
from app.schemas.audit_log import AuditAction, AuditEntityType
from app.schemas.decision import (
    DecisionCreate,
    DecisionResponse,
    DecisionSearchResponse,
    DecisionStatusUpdate,
    DecisionUpdate,
    PaginatedDecisionResponse,
)
from app.services.activity_service import log_activity
from app.services.audit_service import log_audit


router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"],
)


ALLOWED_STATUSES = {
    "Draft",
    "Under Review",
    "Approved",
    "Rejected",
    "Archived",
}


ALLOWED_SORT_FIELDS = {
    "created_at": Decision.created_at,
    "updated_at": Decision.updated_at,
    "title": Decision.title,
}


def get_decision_or_404(
    db: Session,
    decision_id: int,
) -> Decision:
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    return decision


def ensure_decision_access(
    decision: Decision,
    current_user: User,
) -> None:
    """
    Verify that the authenticated user has permission to access
    the decision.

    Employees may access their own decisions.
    Reviewers, Managers and Administrators may access decisions
    available to their role.
    """

    if current_user.role == "Employee":
        if decision.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own decisions",
            )
        return

    if current_user.role in {
        "Reviewer",
        "Manager",
        "Administrator",
    }:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Insufficient permissions",
    )


def validate_required_decision_fields(
    title: str,
    problem_statement: str,
    category: str,
) -> None:
    if not title or not title.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Decision title cannot be empty",
        )

    if not problem_statement or not problem_statement.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Problem statement cannot be empty",
        )

    if not category or not category.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Decision category cannot be empty",
        )


def get_next_version_number(
    db: Session,
    decision_id: int,
) -> int:
    latest_version = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision_id,
        )
        .order_by(
            DecisionVersion.version_number.desc(),
        )
        .first()
    )

    if latest_version:
        return latest_version.version_number + 1

    return 1


def create_decision_version(
    db: Session,
    decision: Decision,
    changed_by: int,
    change_summary: str,
) -> DecisionVersion:
    version = DecisionVersion(
        decision_id=decision.id,
        version_number=get_next_version_number(
            db,
            decision.id,
        ),
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status=decision.status,
        changed_by=changed_by,
        change_summary=change_summary,
    )

    db.add(version)
    return version


# ---------------------------------------------------------------------------
# CREATE DECISION
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=DecisionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_decision(
    decision_data: DecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_required_decision_fields(
        decision_data.title,
        decision_data.problem_statement,
        decision_data.category,
    )

    if current_user.role not in {
        "Employee",
        "Reviewer",
        "Manager",
        "Administrator",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create decisions",
        )

    decision = Decision(
        title=decision_data.title.strip(),
        problem_statement=decision_data.problem_statement.strip(),
        category=decision_data.category.strip(),
        tags=(
            decision_data.tags.strip()
            if decision_data.tags
            else None
        ),
        status="Draft",
        created_by=current_user.id,
    )

    db.add(decision)
    db.flush()

    create_decision_version(
        db=db,
        decision=decision,
        changed_by=current_user.id,
        change_summary="Decision created",
    )

    log_audit(
        db=db,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type=AuditEntityType.DECISION,
        entity_id=decision.id,
        description=f"Decision '{decision.title}' created",
        new_value={
            "title": decision.title,
            "problem_statement": decision.problem_statement,
            "category": decision.category,
            "tags": decision.tags,
            "status": decision.status,
        },
        request_method="POST",
        endpoint="/decisions",
    )

    log_activity(
        db,
        current_user.id,
        "Decision Created",
        "Decision",
        decision.id,
        f"Decision '{decision.title}' created",
    )

    db.commit()
    db.refresh(decision)

    return decision


# ---------------------------------------------------------------------------
# KNOWLEDGE REPOSITORY / SEARCH
# ---------------------------------------------------------------------------

@router.get(
    "/search",
    response_model=PaginatedDecisionResponse,
)
def search_decisions(
    q: Optional[str] = Query(
        default=None,
        min_length=1,
    ),
    category: Optional[str] = Query(
        default=None,
        min_length=1,
    ),
    status_filter: Optional[str] = Query(
        default=None,
        alias="status",
    ),
    tag: Optional[str] = Query(
        default=None,
        min_length=1,
    ),
    date_from: Optional[datetime] = Query(
        default=None,
    ),
    date_to: Optional[datetime] = Query(
        default=None,
    ),
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    sort: str = Query(
        default="created_at",
    ),
    order: str = Query(
        default="desc",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if status_filter:
        status_filter = status_filter.strip()

        if status_filter not in ALLOWED_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid decision status",
            )

    if sort:
        sort = sort.strip()

    if sort not in ALLOWED_SORT_FIELDS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Invalid sort field. Allowed values: "
                "created_at, updated_at, title"
            ),
        )

    normalized_order = order.strip().lower()

    if normalized_order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid sort order. Use 'asc' or 'desc'",
        )

    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="date_from cannot be later than date_to",
        )

    query = db.query(Decision)

    # Employees only see their own decisions.
    if current_user.role == "Employee":
        query = query.filter(
            Decision.created_by == current_user.id,
        )

    elif current_user.role not in {
        "Reviewer",
        "Manager",
        "Administrator",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    if status_filter:
        query = query.filter(
            Decision.status == status_filter,
        )

    if category:
        category_value = category.strip()

        if category_value:
            query = query.filter(
                Decision.category.ilike(category_value),
            )

    if q:
        search_value = q.strip()

        if search_value:
            search_pattern = f"%{search_value}%"

            query = query.filter(
                or_(
                    Decision.title.ilike(search_pattern),
                    Decision.problem_statement.ilike(
                        search_pattern,
                    ),
                    Decision.category.ilike(search_pattern),
                    Decision.tags.ilike(search_pattern),
                )
            )

    if tag:
        tag_value = tag.strip()

        if tag_value:
            tag_pattern = f"%{tag_value}%"

            query = query.filter(
                Decision.tags.ilike(tag_pattern),
            )

    if date_from:
        query = query.filter(
            Decision.created_at >= date_from,
        )

    if date_to:
        query = query.filter(
            Decision.created_at <= date_to,
        )

    total = query.count()

    sort_column = ALLOWED_SORT_FIELDS[sort]

    if normalized_order == "asc":
        query = query.order_by(
            sort_column.asc(),
            Decision.id.asc(),
        )
    else:
        query = query.order_by(
            sort_column.desc(),
            Decision.id.desc(),
        )

    offset = (page - 1) * page_size

    decisions = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    items = [
        DecisionSearchResponse.model_validate(
            decision,
        )
        for decision in decisions
    ]

    return PaginatedDecisionResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
    )


# ---------------------------------------------------------------------------
# GET ALL / FILTER DECISIONS
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=List[DecisionResponse],
)
def get_decisions(
    status_filter: Optional[str] = Query(
        default=None,
        alias="status",
    ),
    category: Optional[str] = Query(
        default=None,
    ),
    search: Optional[str] = Query(
        default=None,
        min_length=1,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Decision)

    if current_user.role == "Employee":
        query = query.filter(
            Decision.created_by == current_user.id,
        )

    elif current_user.role not in {
        "Reviewer",
        "Manager",
        "Administrator",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    if status_filter:
        normalized_status = status_filter.strip()

        if normalized_status not in ALLOWED_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid decision status",
            )

        query = query.filter(
            Decision.status == normalized_status,
        )

    if category:
        category_value = category.strip()

        if category_value:
            query = query.filter(
                Decision.category.ilike(category_value),
            )

    if search:
        search_value = search.strip()

        if search_value:
            search_pattern = f"%{search_value}%"

            query = query.filter(
                or_(
                    Decision.title.ilike(search_pattern),
                    Decision.problem_statement.ilike(
                        search_pattern,
                    ),
                    Decision.category.ilike(search_pattern),
                    Decision.tags.ilike(search_pattern),
                )
            )

    return (
        query
        .order_by(
            Decision.updated_at.desc(),
            Decision.id.desc(),
        )
        .all()
    )


# ---------------------------------------------------------------------------
# GET DECISION BY ID
# ---------------------------------------------------------------------------

@router.get(
    "/{decision_id}",
    response_model=DecisionResponse,
)
def get_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        db,
        decision_id,
    )

    ensure_decision_access(
        decision,
        current_user,
    )

    return decision


# ---------------------------------------------------------------------------
# UPDATE DECISION
# ---------------------------------------------------------------------------

@router.put(
    "/{decision_id}",
    response_model=DecisionResponse,
)
def update_decision(
    decision_id: int,
    decision_data: DecisionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        db,
        decision_id,
    )

    validate_required_decision_fields(
        decision_data.title,
        decision_data.problem_statement,
        decision_data.category,
    )

    if current_user.role != "Administrator":
        if (
            decision.created_by != current_user.id
            or decision.status != "Draft"
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the decision owner can edit a draft decision",
            )

    old_values = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category,
        "tags": decision.tags,
        "status": decision.status,
    }

    decision.title = decision_data.title.strip()
    decision.problem_statement = (
        decision_data.problem_statement.strip()
    )
    decision.category = decision_data.category.strip()
    decision.tags = (
        decision_data.tags.strip()
        if decision_data.tags
        else None
    )

    create_decision_version(
        db=db,
        decision=decision,
        changed_by=current_user.id,
        change_summary="Decision updated",
    )

    new_values = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category,
        "tags": decision.tags,
        "status": decision.status,
    }

    log_audit(
        db=db,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type=AuditEntityType.DECISION,
        entity_id=decision.id,
        description=f"Decision '{decision.title}' updated",
        old_value=old_values,
        new_value=new_values,
        request_method="PUT",
        endpoint=f"/decisions/{decision.id}",
    )

    log_activity(
        db,
        current_user.id,
        "Decision Updated",
        "Decision",
        decision.id,
        f"Decision '{decision.title}' updated",
    )

    db.commit()
    db.refresh(decision)

    return decision


# ---------------------------------------------------------------------------
# UPDATE DECISION STATUS
# ---------------------------------------------------------------------------

@router.patch(
    "/{decision_id}/status",
    response_model=DecisionResponse,
)
def update_decision_status(
    decision_id: int,
    status_data: DecisionStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        db,
        decision_id,
    )

    target_status = status_data.status.strip()

    if target_status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid decision status",
        )

    old_status = decision.status

    if target_status == old_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision is already in this status",
        )

    # Employee can only submit their own draft for review.
    if current_user.role == "Employee":
        if (
            decision.created_by != current_user.id
            or old_status != "Draft"
            or target_status != "Under Review"
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Employees can only submit their own "
                    "draft decisions for review"
                ),
            )

    # Administrator can archive a decision.
    elif current_user.role == "Administrator":
        if target_status != "Archived":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Administrators can only archive decisions "
                    "from this endpoint"
                ),
            )

    # Reviewers and Managers must use the approval workflow.
    elif current_user.role in {"Reviewer", "Manager"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Use the approval workflow to change "
                "review or approval status"
            ),
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    decision.status = target_status

    create_decision_version(
        db=db,
        decision=decision,
        changed_by=current_user.id,
        change_summary=(
            f"Status changed from "
            f"{old_status} to {target_status}"
        ),
    )

    action = (
        AuditAction.SUBMIT
        if target_status == "Under Review"
        else AuditAction.UPDATE
    )

    log_audit(
        db=db,
        user_id=current_user.id,
        action=action,
        entity_type=AuditEntityType.DECISION,
        entity_id=decision.id,
        description=(
            f"Decision status changed from "
            f"'{old_status}' to '{target_status}'"
        ),
        old_value={
            "status": old_status,
        },
        new_value={
            "status": target_status,
        },
        request_method="PATCH",
        endpoint=f"/decisions/{decision.id}/status",
    )

    activity_action = (
        "Decision Submitted"
        if target_status == "Under Review"
        else "Decision Archived"
    )

    log_activity(
        db,
        current_user.id,
        activity_action,
        "Decision",
        decision.id,
        (
            f"Decision '{decision.title}' "
            f"moved to {target_status}"
        ),
    )

    db.commit()
    db.refresh(decision)

    return decision


# ---------------------------------------------------------------------------
# DELETE DECISION
# ---------------------------------------------------------------------------

@router.delete(
    "/{decision_id}",
)
def delete_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        db,
        decision_id,
    )

    if current_user.role != "Administrator":
        if (
            decision.created_by != current_user.id
            or decision.status != "Draft"
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Only the owner of a draft decision "
                    "can delete it"
                ),
            )

    old_values = {
        "title": decision.title,
        "status": decision.status,
        "category": decision.category,
    }

    log_audit(
        db=db,
        user_id=current_user.id,
        action=AuditAction.DELETE,
        entity_type=AuditEntityType.DECISION,
        entity_id=decision.id,
        description=f"Decision '{decision.title}' deleted",
        old_value=old_values,
        request_method="DELETE",
        endpoint=f"/decisions/{decision.id}",
    )

    log_activity(
        db,
        current_user.id,
        "Decision Deleted",
        "Decision",
        decision.id,
        f"Decision '{decision.title}' deleted",
    )

    db.delete(decision)
    db.commit()

    return {
        "message": "Decision deleted successfully",
        "decision_id": decision_id,
    }


# ---------------------------------------------------------------------------
# GET DECISION VERSION HISTORY
# ---------------------------------------------------------------------------

@router.get(
    "/{decision_id}/history",
)
def get_decision_history(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        db,
        decision_id,
    )

    ensure_decision_access(
        decision,
        current_user,
    )

    versions = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision_id,
        )
        .order_by(
            DecisionVersion.version_number.asc(),
        )
        .all()
    )

    return [
        {
            "id": version.id,
            "decision_id": version.decision_id,
            "version_number": version.version_number,
            "title": version.title,
            "problem_statement": version.problem_statement,
            "category": version.category,
            "status": version.status,
            "changed_by": version.changed_by,
            "change_summary": version.change_summary,
            "created_at": version.created_at,
        }
        for version in versions
    ]


# ---------------------------------------------------------------------------
# COMPARE DECISION VERSIONS
# ---------------------------------------------------------------------------

@router.get(
    "/{decision_id}/versions/compare",
)
def compare_decision_versions(
    decision_id: int,
    version_a: int = Query(
        ...,
        ge=1,
    ),
    version_b: int = Query(
        ...,
        ge=1,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        db,
        decision_id,
    )

    ensure_decision_access(
        decision,
        current_user,
    )

    if version_a == version_b:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Select two different versions to compare",
        )

    first_version = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision_id,
            DecisionVersion.version_number == version_a,
        )
        .first()
    )

    second_version = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision_id,
            DecisionVersion.version_number == version_b,
        )
        .first()
    )

    if not first_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_a} not found",
        )

    if not second_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_b} not found",
        )

    differences = {}

    if first_version.title != second_version.title:
        differences["title"] = {
            "version_a": first_version.title,
            "version_b": second_version.title,
        }

    if (
        first_version.problem_statement
        != second_version.problem_statement
    ):
        differences["problem_statement"] = {
            "version_a": first_version.problem_statement,
            "version_b": second_version.problem_statement,
        }

    if first_version.category != second_version.category:
        differences["category"] = {
            "version_a": first_version.category,
            "version_b": second_version.category,
        }

    if first_version.status != second_version.status:
        differences["status"] = {
            "version_a": first_version.status,
            "version_b": second_version.status,
        }

    return {
        "decision_id": decision_id,
        "version_a": version_a,
        "version_b": version_b,
        "differences": differences,
    }


# ---------------------------------------------------------------------------
# GET SPECIFIC DECISION VERSION
# ---------------------------------------------------------------------------

@router.get(
    "/{decision_id}/versions/{version_number}",
)
def get_decision_version(
    decision_id: int,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        db,
        decision_id,
    )

    ensure_decision_access(
        decision,
        current_user,
    )

    if version_number < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Version number must be at least 1",
        )

    version = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision_id,
            DecisionVersion.version_number == version_number,
        )
        .first()
    )

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision version not found",
        )

    return {
        "id": version.id,
        "decision_id": version.decision_id,
        "version_number": version.version_number,
        "title": version.title,
        "problem_statement": version.problem_statement,
        "category": version.category,
        "status": version.status,
        "changed_by": version.changed_by,
        "change_summary": version.change_summary,
        "created_at": version.created_at,
    }