from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, asc, desc

from app.core.activity_logger import create_activity_log
from app.core.dependencies import get_current_user

from app.db.database import get_db

from app.models.decision import Decision
from app.models.tag import Tag
from app.models.user import User

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

from app.core.dependencies import (
    get_current_user,
    require_admin,
)

from app.core.activity_logger import create_activity_log


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

    # Activity log for decision creation
    create_activity_log(
        db=db,
        user=current_user,
        action="CREATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"Created decision: {decision.title}"
    )

    db.commit()

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

    # -----------------------------------------------------
    # KEYWORD SEARCH
    # -----------------------------------------------------

    if search:
        search_pattern = f"%{search}%"

        query = query.filter(
            or_(
                Decision.title.ilike(search_pattern),
                Decision.problem_statement.ilike(search_pattern)
            )
        )

    # -----------------------------------------------------
    # STATUS FILTER
    # -----------------------------------------------------

    if status_filter:
        query = query.filter(
            Decision.status == status_filter.value
        )

    # -----------------------------------------------------
    # CATEGORY FILTER
    # -----------------------------------------------------

    if category:
        query = query.filter(
            Decision.category == category
        )

    # -----------------------------------------------------
    # TAG FILTER
    # -----------------------------------------------------

    if tag:
        query = query.join(
            Decision.tags
        ).filter(
            Tag.name == tag
        )

    # -----------------------------------------------------
    # CONTROLLED SORTING
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # PAGINATION
    # -----------------------------------------------------

    offset = (page - 1) * limit

    query = query.offset(offset).limit(limit)

    return query.all()


# =========================================================
# TASK 11 / TASK 20 - DECISION SEARCH
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

    # -----------------------------------------------------
    # CATEGORY FILTER
    # -----------------------------------------------------

    if category:
        query = query.filter(
            Decision.category == category
        )

    # -----------------------------------------------------
    # STATUS FILTER
    # -----------------------------------------------------

    if status_filter:
        query = query.filter(
            Decision.status == status_filter.value
        )

    # -----------------------------------------------------
    # TAG FILTER
    # -----------------------------------------------------

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
# TASK 8 - ASSIGN TAGS TO DECISION
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
# TASK 9 - GET DECISION TAGS
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
# TASK 10 - REMOVE TAG FROM DECISION
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
# TASK 20/23 - DECISION TIMELINE
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

    decision.title = decision_data.title
    decision.problem_statement = decision_data.problem_statement
    decision.category = decision_data.category

    db.commit()
    db.refresh(decision)

    # Activity log for decision update
    create_activity_log(
        db=db,
        user=current_user,
        action="UPDATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"Updated decision: {decision.title}"
    )

    db.commit()

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
    # -----------------------------------------------------
    # Find decision
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Update status
    # -----------------------------------------------------

    decision.status = status_data.status.value

    # -----------------------------------------------------
    # Create activity log
    # -----------------------------------------------------

    create_activity_log(
        db=db,
        user=current_user,
        action="STATUS_CHANGE",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"Changed decision status to {decision.status}"
    )

    # -----------------------------------------------------
    # Save changes
    # -----------------------------------------------------

    db.commit()
    db.refresh(decision)

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

    decision.rationale = rationale_data.rationale

    db.commit()
    db.refresh(decision)

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

    db.delete(decision)
    db.commit()

    return {
        "message": "Decision deleted successfully"
    }