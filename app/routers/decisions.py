from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db

from app.models.activity_log import ActivityLog
from app.models.decision import Decision
from app.models.decision_status import DecisionStatus
from app.models.decision_timeline import DecisionTimeline
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

from app.services.activity_log import create_activity_log


router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)


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

    # Create timeline event
    timeline_event = DecisionTimeline(
        decision_id=new_decision.id,
        event_type="created",
        description="Decision was created"
    )

    db.add(timeline_event)

    # Create activity log
    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="created",
        entity_type="decision",
        entity_id=new_decision.id,
        description=f"Created decision: {new_decision.title}"
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

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total
    }


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

    # Only create logs if something was actually updated
    if updated_fields:

        timeline_event = DecisionTimeline(
            decision_id=decision.id,
            event_type="updated",
            description="Updated: " + ", ".join(updated_fields)
        )

        db.add(timeline_event)

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

    decision.status = new_status

    # Create timeline event
    timeline_event = DecisionTimeline(
        decision_id=decision.id,
        event_type="status_changed",
        description=(
            f"Status changed from "
            f"{old_status.value} to "
            f"{new_status.value}"
        )
    )

    db.add(timeline_event)

    # Create activity log
    create_activity_log(
        db=db,
        user_id=current_user.id,
        action="status_changed",
        entity_type="decision",
        entity_id=decision.id,
        description=(
            f"Changed decision status from "
            f"{old_status.value} to "
            f"{new_status.value}: "
            f"{decision.title}"
        )
    )

    db.commit()
    db.refresh(decision)

    return decision