from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.audit import AuditAction, AuditLog, DecisionVersion
from app.models.decision import Decision, DecisionStatus
from app.models.tag import Tag
from app.models.user import User, UserRole
from app.schemas.audit import DecisionVersionResponse, TimelineResponse
from app.schemas.decision import (
    DecisionCreate,
    DecisionHistoryItem,
    DecisionListResponse,
    DecisionRationaleUpdate,
    DecisionResponse,
    DecisionSearchResponse,
    DecisionSearchResult,
    DecisionStatusUpdate,
    DecisionUpdate,
)
from app.schemas.decision_detail import DecisionDetailResponse
from app.schemas.tag import DecisionTagCreate, TagResponse
from app.services.audit import (
    create_access_log,
    create_audit_log,
    create_decision_version,
)
from app.services.auth import get_current_user


router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"],
)


# ============================================================
# ORGANIZATION ACCESS HELPERS
# ============================================================

def can_access_decision(
    decision: Decision,
    current_user: User,
) -> bool:
    """
    A user can access a decision only if:

    1. The decision belongs to the user's organization.
    2. The user is:
       - the creator, or
       - a Manager, or
       - an Administrator.
    """

    if decision.organization_id != current_user.organization_id:
        return False

    return (
        decision.created_by == current_user.id
        or current_user.role in (
            UserRole.MANAGER,
            UserRole.ADMINISTRATOR,
        )
    )


def can_modify_decision(
    decision: Decision,
    current_user: User,
) -> bool:
    """
    A user can modify a decision only if it belongs
    to the same organization and the user is authorized.
    """

    return can_access_decision(
        decision,
        current_user,
    )


def get_decision_or_404(
    decision_id: int,
    db: Session,
    current_user: User,
) -> Decision:
    """
    Fetch a decision and enforce organization isolation.
    """

    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    if decision.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    return decision


# ============================================================
# CREATE DECISION
# ============================================================

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
    """
    Create a decision inside the current user's organization.
    """

    if current_user.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not assigned to an organization",
        )

    decision = Decision(
        title=decision_data.title,
        problem_statement=decision_data.problem_statement,
        category=decision_data.category,
        rationale=getattr(
            decision_data,
            "rationale",
            None,
        ),
        status=DecisionStatus.DRAFT,
        created_by=current_user.id,
        organization_id=current_user.organization_id,
    )

    db.add(decision)
    db.flush()

    create_audit_log(
        db=db,
        decision_id=decision.id,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"Decision '{decision.title}' was created"
        ),
    )

    create_decision_version(
        db=db,
        decision=decision,
        user_id=current_user.id,
    )

    db.commit()
    db.refresh(decision)

    return decision


# ============================================================
# SEARCH DECISIONS
# Dedicated discovery search endpoint
# ============================================================

@router.get(
    "/search",
    response_model=DecisionSearchResponse,
)
def search_decisions(
    q: str | None = Query(
        default=None,
        description="Search query across title, problem statement, rationale",
    ),
    keyword: str | None = Query(
        default=None,
        description="Search keyword alias",
    ),
    category: str | None = Query(
        default=None,
        description="Filter by category",
    ),
    status_filter: DecisionStatus | None = Query(
        default=None,
        alias="status",
        description="Filter by status",
    ),
    tag: str | None = Query(
        default=None,
        description="Filter by tag name",
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
    sort_by: str = Query(
        default="created_at",
        description="created_at, updated_at or title",
    ),
    sort_order: str = Query(
        default="desc",
        description="asc or desc",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not assigned to an organization",
        )

    query = (
        db.query(Decision)
        .filter(
            Decision.organization_id
            == current_user.organization_id
        )
    )

    search_term = q or keyword
    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            or_(
                Decision.title.ilike(search_pattern),
                Decision.problem_statement.ilike(search_pattern),
                Decision.rationale.ilike(search_pattern),
            )
        )

    if status_filter is not None:
        query = query.filter(
            Decision.status == status_filter
        )

    if category is not None:
        query = query.filter(
            Decision.category == category
        )

    if tag is not None:
        query = (
            query
            .join(Decision.tags)
            .filter(
                Tag.name == tag,
                Tag.organization_id
                == current_user.organization_id,
            )
        )

    total = query.count()

    if sort_by == "title":
        sort_column = Decision.title
    elif sort_by == "updated_at":
        sort_column = Decision.updated_at
    elif sort_by == "created_at":
        sort_column = Decision.created_at
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sort_by. Use created_at, updated_at or title",
        )

    if sort_order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    elif sort_order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sort_order. Use asc or desc",
        )

    offset = (page - 1) * page_size
    decisions = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    total_pages = ceil(total / page_size) if total > 0 else 0

    results = [
        DecisionSearchResult(
            id=d.id,
            title=d.title,
            problem_statement=d.problem_statement,
            category=d.category,
            status=d.status.value if hasattr(d.status, "value") else str(d.status),
            tags=[t.name for t in d.tags],
            created_at=d.created_at,
            updated_at=d.updated_at,
        )
        for d in decisions
    ]

    return DecisionSearchResponse(
        results=results,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# ============================================================
# GET ALL DECISIONS
# Search, filters, pagination and sorting
# Organization isolated
# ============================================================

@router.get(
    "",
    response_model=DecisionListResponse,
)
def get_decisions(
    q: str | None = Query(
        default=None,
        description="Search query string alias",
    ),
    keyword: str | None = Query(
        default=None,
        description=(
            "Search in title, problem statement and rationale"
        ),
    ),
    status_filter: DecisionStatus | None = Query(
        default=None,
        alias="status",
    ),
    category: str | None = None,
    tag: str | None = Query(
        default=None,
        description="Filter by tag name",
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
    sort_by: str = Query(
        default="created_at",
        description="created_at, updated_at or title",
    ),
    sort_order: str = Query(
        default="desc",
        description="asc or desc",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return decisions belonging only to the current user's organization.
    """

    if current_user.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not assigned to an organization",
        )

    query = (
        db.query(Decision)
        .filter(
            Decision.organization_id
            == current_user.organization_id
        )
    )

    # --------------------------------------------------------
    # Keyword / query search
    # --------------------------------------------------------

    search_term = q or keyword
    if search_term:
        search_pattern = f"%{search_term}%"

        query = query.filter(
            or_(
                Decision.title.ilike(search_pattern),
                Decision.problem_statement.ilike(
                    search_pattern
                ),
                Decision.rationale.ilike(
                    search_pattern
                ),
            )
        )

    # --------------------------------------------------------
    # Status filter
    # --------------------------------------------------------

    if status_filter is not None:
        query = query.filter(
            Decision.status == status_filter
        )

    # --------------------------------------------------------
    # Category filter
    # --------------------------------------------------------

    if category is not None:
        query = query.filter(
            Decision.category == category
        )

    # --------------------------------------------------------
    # Tag filter
    # --------------------------------------------------------

    if tag is not None:
        query = (
            query
            .join(Decision.tags)
            .filter(
                Tag.name == tag,
                Tag.organization_id
                == current_user.organization_id,
            )
        )

    # --------------------------------------------------------
    # Total results
    # --------------------------------------------------------

    total = query.count()

    # --------------------------------------------------------
    # Sorting
    # --------------------------------------------------------

    if sort_by == "title":
        sort_column = Decision.title

    elif sort_by == "updated_at":
        sort_column = Decision.updated_at

    elif sort_by == "created_at":
        sort_column = Decision.created_at

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid sort_by. "
                "Use created_at, updated_at or title"
            ),
        )

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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sort_order. Use asc or desc",
        )

    # --------------------------------------------------------
    # Pagination
    # --------------------------------------------------------

    offset = (page - 1) * page_size

    decisions = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    total_pages = (
        ceil(total / page_size)
        if total > 0
        else 0
    )

    return DecisionListResponse(
        items=decisions,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )



# ============================================================
# UPDATE DECISION RATIONALE
# ============================================================

@router.put(
    "/{decision_id}/rationale",
    response_model=DecisionResponse,
)
def update_decision_rationale(
    decision_id: int,
    rationale_data: DecisionRationaleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        decision_id,
        db,
        current_user,
    )

    if not can_modify_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to modify this decision"
            ),
        )

    if decision.status == DecisionStatus.ARCHIVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify an archived decision",
        )

    old_value = {"rationale": decision.rationale}
    decision.rationale = rationale_data.rationale
    new_value = {"rationale": decision.rationale}

    create_audit_log(
        db=db,
        decision_id=decision.id,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"Rationale updated for decision "
            f"'{decision.title}'"
        ),
        old_value=old_value,
        new_value=new_value,
    )

    create_decision_version(
        db=db,
        decision=decision,
        user_id=current_user.id,
    )

    db.commit()
    db.refresh(decision)

    return decision


# ============================================================
# ASSIGN TAGS TO DECISION
# ============================================================

@router.post(
    "/{decision_id}/tags",
    response_model=list[TagResponse],
    status_code=status.HTTP_201_CREATED,
)
def assign_tags_to_decision(
    decision_id: int,
    tag_data: DecisionTagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        decision_id,
        db,
        current_user,
    )

    if not can_modify_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to modify this decision"
            ),
        )

    if decision.status == DecisionStatus.ARCHIVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify an archived decision",
        )

    # Remove duplicate IDs
    tag_ids = list(
        dict.fromkeys(tag_data.tag_ids)
    )

    if not tag_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one tag ID is required",
        )

    # IMPORTANT:
    # Only retrieve tags belonging to the same organization.
    tags = (
        db.query(Tag)
        .filter(
            Tag.id.in_(tag_ids),
            Tag.organization_id
            == current_user.organization_id,
        )
        .all()
    )

    found_tag_ids = {
        tag.id
        for tag in tags
    }

    missing_tag_ids = [
        tag_id
        for tag_id in tag_ids
        if tag_id not in found_tag_ids
    ]

    if missing_tag_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Tag(s) not found in your organization: "
                f"{missing_tag_ids}"
            ),
        )

    existing_tag_ids = {
        tag.id
        for tag in decision.tags
    }

    already_assigned = [
        tag_id
        for tag_id in tag_ids
        if tag_id in existing_tag_ids
    ]

    if already_assigned:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Tag(s) already assigned to this decision: "
                f"{already_assigned}"
            ),
        )

    decision.tags.extend(tags)

    # Audit each tag assignment
    for tag in tags:
        create_audit_log(
            db=db,
            decision_id=decision.id,
            user_id=current_user.id,
            action=AuditAction.TAG_ADDED,
            entity_type="Tag",
            entity_id=tag.id,
            description=(
                f"Tag '{tag.name}' was added to "
                f"decision '{decision.title}'"
            ),
        )

    db.commit()

    return tags


# ============================================================
# GET TAGS ASSIGNED TO DECISION
# ============================================================

@router.get(
    "/{decision_id}/tags",
    response_model=list[TagResponse],
)
def get_decision_tags(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        decision_id,
        db,
        current_user,
    )

    return decision.tags


# ============================================================
# REMOVE TAG FROM DECISION
# ============================================================

@router.delete(
    "/{decision_id}/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_tag_from_decision(
    decision_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        decision_id,
        db,
        current_user,
    )

    if not can_modify_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to modify this decision"
            ),
        )

    if decision.status == DecisionStatus.ARCHIVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify an archived decision",
        )

    # Tag must belong to the same organization
    tag = (
        db.query(Tag)
        .filter(
            Tag.id == tag_id,
            Tag.organization_id
            == current_user.organization_id,
        )
        .first()
    )

    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    if tag not in decision.tags:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag is not assigned to this decision",
        )

    tag_name = tag.name

    decision.tags.remove(tag)

    create_audit_log(
        db=db,
        decision_id=decision.id,
        user_id=current_user.id,
        action=AuditAction.TAG_REMOVED,
        entity_type="Tag",
        entity_id=tag.id,
        description=(
            f"Tag '{tag_name}' was removed from "
            f"decision '{decision.title}'"
        ),
    )

    db.commit()

    return None


# ============================================================
# GET COMPLETE DECISION DETAILS
# ============================================================

@router.get(
    "/{decision_id}/detail",
    response_model=DecisionDetailResponse,
)
def get_decision_detail(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        decision_id,
        db,
        current_user,
    )

    if not can_access_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to view this decision"
            ),
        )

    return decision


# ============================================================
# GET DECISION TIMELINE
# ============================================================

@router.get(
    "/{decision_id}/timeline",
    response_model=list[TimelineResponse],
)
def get_decision_timeline(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        decision_id,
        db,
        current_user,
    )

    if not can_access_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to view this decision"
            ),
        )

    timeline = (
        db.query(AuditLog)
        .filter(
            AuditLog.decision_id == decision_id
        )
        .order_by(
            AuditLog.created_at.asc()
        )
        .all()
    )

    return timeline


# ============================================================
# GET DECISION VERSIONS
# ============================================================

@router.get(
    "/{decision_id}/versions",
    response_model=list[DecisionVersionResponse],
)
def get_decision_versions(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        decision_id,
        db,
        current_user,
    )

    if not can_access_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to view versions for this decision"
            ),
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


# ============================================================
# GET SPECIFIC DECISION VERSION
# ============================================================

@router.get(
    "/{decision_id}/versions/{version_number}",
    response_model=DecisionVersionResponse,
)
def get_decision_version(
    decision_id: int,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        decision_id,
        db,
        current_user,
    )

    if not can_access_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to view this version"
            ),
        )

    version = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision_id,
            DecisionVersion.version_number == version_number,
        )
        .first()
    )

    if version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_number} not found for decision {decision_id}",
        )

    return version


# ============================================================
# GET DECISION CHANGE HISTORY
# ============================================================

@router.get(
    "/{decision_id}/history",
    response_model=list[DecisionHistoryItem],
)
def get_decision_history(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = get_decision_or_404(
        decision_id,
        db,
        current_user,
    )

    if not can_access_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to view history for this decision"
            ),
        )

    history = (
        db.query(AuditLog)
        .filter(
            AuditLog.decision_id == decision_id
        )
        .order_by(
            AuditLog.created_at.asc()
        )
        .all()
    )

    return history


# ============================================================
# GET DECISION BY ID
# ============================================================

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
        decision_id,
        db,
        current_user,
    )

    if not can_access_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to view this decision"
            ),
        )

    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="Decision",
        resource_id=decision.id,
        action="VIEW",
    )
    db.commit()

    return decision


# ============================================================
# UPDATE DECISION
# ============================================================

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
        decision_id,
        db,
        current_user,
    )

    if not can_modify_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to modify this decision"
            ),
        )

    if decision.status == DecisionStatus.ARCHIVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify an archived decision",
        )

    old_value = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category,
    }

    decision.title = decision_data.title
    decision.problem_statement = decision_data.problem_statement
    decision.category = decision_data.category

    new_value = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category,
    }

    create_audit_log(
        db=db,
        decision_id=decision.id,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"Decision '{decision.title}' was updated"
        ),
        old_value=old_value,
        new_value=new_value,
    )

    create_decision_version(
        db=db,
        decision=decision,
        user_id=current_user.id,
    )

    db.commit()
    db.refresh(decision)

    return decision


# ============================================================
# UPDATE DECISION STATUS
# ============================================================

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
        decision_id,
        db,
        current_user,
    )

    if not can_modify_decision(
        decision,
        current_user,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to modify this decision"
            ),
        )

    old_status = decision.status
    decision.status = status_data.status

    old_value = {
        "status": old_status.value if hasattr(old_status, "value") else str(old_status)
    }
    new_value = {
        "status": decision.status.value if hasattr(decision.status, "value") else str(decision.status)
    }

    create_audit_log(
        db=db,
        decision_id=decision.id,
        user_id=current_user.id,
        action=AuditAction.STATUS_CHANGE,
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"Decision status changed from "
            f"'{old_status.value}' to "
            f"'{decision.status.value}'"
        ),
        old_value=old_value,
        new_value=new_value,
    )

    create_decision_version(
        db=db,
        decision=decision,
        user_id=current_user.id,
    )

    db.commit()
    db.refresh(decision)

    return decision