from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.models.decision import Decision
from app.models.tag import Tag
from app.models.decision_activity import DecisionActivity
from app.models.activity_log import ActivityLog

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

    # Create decision
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

    # -----------------------------------------------------
    # Decision Timeline Activity
    # -----------------------------------------------------

    timeline_activity = DecisionActivity(
        decision_id=new_decision.id,
        activity_type="Created",
        description="Decision created",
        created_by=user_id
    )

    db.add(timeline_activity)

    # -----------------------------------------------------
    # Sprint 10 Activity Log
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Filter by status
    # -----------------------------------------------------

    if status:
        query = query.filter(
            Decision.status == status
        )

    # -----------------------------------------------------
    # Filter by category
    # -----------------------------------------------------

    if category:
        query = query.filter(
            Decision.category == category
        )

    # -----------------------------------------------------
    # Search
    # -----------------------------------------------------

    if search:

        search_pattern = f"%{search}%"

        query = query.filter(
            (Decision.title.ilike(search_pattern)) |
            (Decision.problem_statement.ilike(search_pattern))
        )

    # -----------------------------------------------------
    # Filter by tag
    # -----------------------------------------------------

    if tag:

        query = query.join(
            Decision.tags
        ).filter(
            Tag.name == tag
        )

    # -----------------------------------------------------
    # Pagination validation
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Allowed sorting fields
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Sorting
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Pagination
    # -----------------------------------------------------

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

    db.commit()

    # -----------------------------------------------------
    # Timeline + Activity Log
    # -----------------------------------------------------

    for tag in added_tags:

        # Decision timeline
        timeline_activity = DecisionActivity(
            decision_id=decision.id,
            activity_type="Tag Added",
            description=f"Tag '{tag.name}' added to decision",
            created_by=user_id
        )

        db.add(timeline_activity)

        # Sprint 10 activity log
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

    db.commit()

    # -----------------------------------------------------
    # Timeline Activity
    # -----------------------------------------------------

    timeline_activity = DecisionActivity(
        decision_id=decision.id,
        activity_type="Tag Removed",
        description=f"Tag '{tag_name}' removed from decision",
        created_by=user_id
    )

    db.add(timeline_activity)

    # -----------------------------------------------------
    # Sprint 10 Activity Log
    # -----------------------------------------------------

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
            status_code=404,
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

    decision.title = decision_data.title
    decision.problem_statement = decision_data.problem_statement
    decision.category = decision_data.category

    db.commit()
    db.refresh(decision)

    # -----------------------------------------------------
    # Timeline Activity
    # -----------------------------------------------------

    timeline_activity = DecisionActivity(
        decision_id=decision.id,
        activity_type="Decision Updated",
        description="Decision details updated",
        created_by=user_id
    )

    db.add(timeline_activity)

    # -----------------------------------------------------
    # Sprint 10 Activity Log
    # -----------------------------------------------------

    log = ActivityLog(
        user_id=user_id,
        action="Decision Updated",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"Decision {decision.id} updated"
    )

    db.add(log)

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

    # -----------------------------------------------------
    # Timeline Activity
    # -----------------------------------------------------

    timeline_activity = DecisionActivity(
        decision_id=decision.id,
        activity_type="Status Changed",
        description=f"Status changed from {old_status} to {new_status}",
        created_by=user_id
    )

    db.add(timeline_activity)

    # -----------------------------------------------------
    # Sprint 10 Activity Log
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Timeline Activity
    # -----------------------------------------------------

    timeline_activity = DecisionActivity(
        decision_id=decision.id,
        activity_type="Rationale Updated",
        description="Decision rationale updated",
        created_by=user_id
    )

    db.add(timeline_activity)

    # -----------------------------------------------------
    # Sprint 10 Activity Log
    # -----------------------------------------------------

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