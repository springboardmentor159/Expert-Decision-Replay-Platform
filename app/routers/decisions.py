from typing import Optional, List
from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, or_

from app.db.database import get_db
from app.models.decision import Decision
from app.models.tag import Tag
from app.models.user import User
from app.models.alternative import Alternative
from app.models.comment import Comment
from app.models.discussion_thread import DiscussionThread

from app.core.security import get_current_user
from app.core.enums import DecisionStatus


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
# HELPER
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
    db.commit()
    db.refresh(new_decision)

    return {
        "message": "Decision created successfully",
        "decision": new_decision
    }


# =========================================================
# SEARCH DECISIONS
#
# Supports:
# q
# category
# decision_status
# tag
# page
# page_size
# sort_by
# order
# =========================================================

@router.get("/search")
def search_decisions(

    q: Optional[str] = Query(
        None,
        min_length=1,
        description="Search decision title, problem statement, description, or rationale"
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
        ge=1,
        description="Page number"
    ),

    page_size: int = Query(
        20,
        ge=1,
        le=100,
        description="Number of results per page"
    ),

    sort_by: str = Query(
        "created_at",
        pattern="^(created_at|updated_at|title)$",
        description="created_at, updated_at, or title"
    ),

    order: str = Query(
        "desc",
        pattern="^(asc|desc)$",
        description="asc or desc"
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):

    query = db.query(Decision)

    # -----------------------------------------------------
    # KEYWORD SEARCH
    # -----------------------------------------------------

    if q:

        search_value = f"%{q}%"

        query = query.filter(
            or_(
                Decision.title.ilike(search_value),
                Decision.problem_statement.ilike(search_value),
                Decision.rationale.ilike(search_value)
            )
        )

    # -----------------------------------------------------
    # CATEGORY FILTER
    # -----------------------------------------------------

    if category:

        query = query.filter(
            Decision.category.ilike(category)
        )

    # -----------------------------------------------------
    # STATUS FILTER
    # -----------------------------------------------------

    if decision_status:

        query = query.filter(
            Decision.status == decision_status
        )

    # -----------------------------------------------------
    # TAG FILTER
    # -----------------------------------------------------

    if tag:

        query = query.join(
            Decision.tags
        ).filter(
            Tag.name.ilike(tag)
        ).distinct()

    # -----------------------------------------------------
    # TOTAL
    # -----------------------------------------------------

    total = query.count()

    # -----------------------------------------------------
    # SORTING
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # PAGINATION
    # -----------------------------------------------------

    offset = (page - 1) * page_size

    decisions = query.offset(
        offset
    ).limit(
        page_size
    ).all()

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

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
#
# Supports:
# search
# category
# decision_status
# tag
# pagination
# sorting
# =========================================================

@router.get("/")
def get_all_decisions(

    search: Optional[str] = Query(
        None,
        description="Search by title, problem statement, or rationale"
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
        ge=1,
        description="Page number"
    ),

    page_size: int = Query(
        20,
        ge=1,
        le=100,
        description="Number of results per page"
    ),

    sort_by: str = Query(
        "created_at",
        pattern="^(created_at|updated_at|title)$",
        description="created_at, updated_at, or title"
    ),

    order: str = Query(
        "desc",
        pattern="^(asc|desc)$",
        description="asc or desc"
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):

    query = db.query(Decision)

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    if search:

        search_value = f"%{search}%"

        query = query.filter(
            or_(
                Decision.title.ilike(search_value),
                Decision.problem_statement.ilike(search_value),
                Decision.rationale.ilike(search_value)
            )
        )

    # -----------------------------------------------------
    # CATEGORY
    # -----------------------------------------------------

    if category:

        query = query.filter(
            Decision.category.ilike(category)
        )

    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------

    if decision_status:

        query = query.filter(
            Decision.status == decision_status
        )

    # -----------------------------------------------------
    # TAG
    # -----------------------------------------------------

    if tag:

        query = query.join(
            Decision.tags
        ).filter(
            Tag.name.ilike(tag)
        ).distinct()

    # -----------------------------------------------------
    # COUNT
    # -----------------------------------------------------

    total = query.count()

    # -----------------------------------------------------
    # SORTING
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # PAGINATION
    # -----------------------------------------------------

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

    return get_decision_or_404(
        decision_id,
        db
    )


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

    update_data = decision_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():

        setattr(
            decision,
            field,
            value
        )

    db.commit()
    db.refresh(decision)

    return {
        "message": "Decision updated successfully",
        "decision": decision
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

    db.delete(decision)
    db.commit()

    return {
        "message": "Decision deleted successfully"
    }


# =========================================================
# ASSIGN TAGS TO DECISION
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

    # -----------------------------------------------------
    # REMOVE DUPLICATE IDS FROM REQUEST
    # -----------------------------------------------------

    requested_tag_ids = set(
        tag_data.tag_ids
    )

    if not requested_tag_ids:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one tag ID is required"
        )

    # -----------------------------------------------------
    # FIND TAGS
    # -----------------------------------------------------

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
            detail=f"Tags not found: {list(missing_tag_ids)}"
        )

    # -----------------------------------------------------
    # ASSIGN TAGS
    # -----------------------------------------------------

    for tag in tags:

        if tag not in decision.tags:

            decision.tags.append(tag)

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
# REMOVE TAG FROM DECISION
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
            detail="This tag is not assigned to this decision"
        )

    decision.tags.remove(tag)

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
    # NORMALIZE TIMESTAMPS
    # -----------------------------------------------------

    def normalize_timestamp(timestamp):

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

    # -----------------------------------------------------
    # DECISION CREATED
    # -----------------------------------------------------

    timeline.append({
        "event_type": "Decision created",
        "description": f"Decision '{decision.title}' was created",
        "timestamp": decision.created_at
    })

    # -----------------------------------------------------
    # DECISION UPDATED
    # -----------------------------------------------------

    if decision.updated_at:

        if normalize_timestamp(
            decision.updated_at
        ) != normalize_timestamp(
            decision.created_at
        ):

            timeline.append({
                "event_type": "Decision updated",
                "description": f"Decision '{decision.title}' was updated",
                "timestamp": decision.updated_at
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
            "description": f"Alternative '{alternative.name}' was added",
            "timestamp": alternative.created_at
        })

        if alternative.updated_at:

            if normalize_timestamp(
                alternative.updated_at
            ) != normalize_timestamp(
                alternative.created_at
            ):

                timeline.append({
                    "event_type": "Alternative updated",
                    "description": f"Alternative '{alternative.name}' was updated",
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
            "description": "A comment was added to the decision",
            "timestamp": comment.created_at
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
            "description": f"Discussion thread '{thread.title}' was created",
            "timestamp": thread.created_at
        })

    # -----------------------------------------------------
    # STATUS EVENTS
    # -----------------------------------------------------

    if decision.status == DecisionStatus.APPROVED:

        timeline.append({
            "event_type": "Decision approved",
            "description": "Decision status is Approved",
            "timestamp": decision.updated_at
        })

    elif decision.status == DecisionStatus.REJECTED:

        timeline.append({
            "event_type": "Decision rejected",
            "description": "Decision status is Rejected",
            "timestamp": decision.updated_at
        })

    elif decision.status == DecisionStatus.ARCHIVED:

        timeline.append({
            "event_type": "Decision archived",
            "description": "Decision status is Archived",
            "timestamp": decision.updated_at
        })

    # -----------------------------------------------------
    # SORT CHRONOLOGICALLY
    # -----------------------------------------------------

    timeline.sort(
        key=lambda event: normalize_timestamp(
            event["timestamp"]
        )
    )

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {
        "decision_id": decision_id,
        "timeline": timeline
    }