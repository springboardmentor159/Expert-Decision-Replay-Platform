from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.models.tag import Tag
from app.schemas.decision import (
    DecisionCreate,
    DecisionResponse,
    DecisionUpdate,
    DecisionStatus,
    DecisionStatusUpdate,
    DecisionRationaleUpdate,
    DecisionRationaleResponse,
    DecisionSearchResult,
    PaginatedDecisions,
    DecisionTimelineResponse,
)
from app.schemas.tag import TagResponse, TagAssignRequest
from app.utils.security import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)


# ---------------------------------------------------------------------
# Sprint 9: Knowledge Repository helpers
# ---------------------------------------------------------------------

# Controlled list of columns that may be sorted on. Never let the raw
# query-string value reach the database directly.
ALLOWED_SORT_FIELDS = {
    "created_at": Decision.created_at,
    "updated_at": Decision.updated_at,
    "title": Decision.title,
}


def _apply_decision_filters(
    query,
    category: Optional[str],
    status_filter: Optional[DecisionStatus],
    tag: Optional[str],
    keyword: Optional[str],
):
    if category is not None:
        query = query.filter(Decision.category == category)

    if status_filter is not None:
        query = query.filter(Decision.status == status_filter.value)

    if tag is not None:
        query = query.join(Decision.tags).filter(Tag.name == tag)

    if keyword is not None:
        like_pattern = f"%{keyword}%"
        query = query.filter(
            or_(
                Decision.title.ilike(like_pattern),
                Decision.problem_statement.ilike(like_pattern),
                Decision.rationale.ilike(like_pattern),
            )
        )

    return query


def _validate_sort(sort: str, order: str):
    if sort not in ALLOWED_SORT_FIELDS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Invalid sort field. Allowed values: "
                f"{', '.join(ALLOWED_SORT_FIELDS)}"
            )
        )

    if order not in ("asc", "desc"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid order. Allowed values: asc, desc"
        )


def _apply_sorting(query, sort: str, order: str):
    column = ALLOWED_SORT_FIELDS[sort]
    return query.order_by(column.asc() if order == "asc" else column.desc())


def _paginate(query, page: int, page_size: int):
    total = query.distinct().count()

    items = (
        query
        .distinct()
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return items, total


def get_decision_or_404(decision_id: int, db: Session) -> Decision:
    decision = db.query(Decision).filter(Decision.id == decision_id).first()

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return decision


# CREATE DECISION
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
        status=DecisionStatus.DRAFT.value,
        created_by=current_user.id
    )

    db.add(new_decision)
    db.commit()
    db.refresh(new_decision)

    return new_decision


# GET ALL DECISIONS (filtering + pagination + sorting)
@router.get(
    "",
    response_model=PaginatedDecisions
)
def get_decisions(
    status_filter: Optional[DecisionStatus] = Query(
        default=None,
        alias="status",
        description="Filter decisions by status"
    ),
    category: Optional[str] = Query(
        default=None,
        description="Filter decisions by category"
    ),
    tag: Optional[str] = Query(
        default=None,
        description="Filter decisions by tag name"
    ),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    sort: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _validate_sort(sort, order)

    query = db.query(Decision)
    query = _apply_decision_filters(query, category, status_filter, tag, None)
    query = _apply_sorting(query, sort, order)

    items, total = _paginate(query, page, page_size)

    return PaginatedDecisions(
        items=[DecisionSearchResult.model_validate(d) for d in items],
        page=page,
        page_size=page_size,
        total=total,
    )


# Sprint 9: DECISION SEARCH (keyword + category + status + tag, combined)
# NOTE: this must be declared BEFORE "/{decision_id}" so that FastAPI
# does not try to interpret "search" as a decision_id.
@router.get(
    "/search",
    response_model=PaginatedDecisions
)
def search_decisions(
    q: Optional[str] = Query(
        default=None,
        description="Keyword to search in title, problem statement and rationale"
    ),
    category: Optional[str] = Query(default=None),
    status_filter: Optional[DecisionStatus] = Query(default=None, alias="status"),
    tag: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    sort: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _validate_sort(sort, order)

    query = db.query(Decision)
    query = _apply_decision_filters(query, category, status_filter, tag, q)
    query = _apply_sorting(query, sort, order)

    items, total = _paginate(query, page, page_size)

    return PaginatedDecisions(
        items=[DecisionSearchResult.model_validate(d) for d in items],
        page=page,
        page_size=page_size,
        total=total,
    )


# GET DECISION BY ID
@router.get(
    "/{decision_id}",
    response_model=DecisionResponse
)
def get_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_decision_or_404(decision_id, db)


# UPDATE DECISION
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
    decision = get_decision_or_404(decision_id, db)

    # Sprint 9: archived decisions should not be casually modified.
    if decision.status == DecisionStatus.ARCHIVED.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Archived decisions cannot be modified"
        )

    # Only allowed fields can be updated.
    # id, created_by, created_at are never touched here.
    if decision_data.title is not None:
        decision.title = decision_data.title

    if decision_data.problem_statement is not None:
        decision.problem_statement = decision_data.problem_statement

    if decision_data.category is not None:
        decision.category = decision_data.category

    decision.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(decision)

    return decision


# UPDATE DECISION STATUS
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
    decision = get_decision_or_404(decision_id, db)

    decision.status = status_data.status.value
    decision.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(decision)

    return decision


# Sprint 7: SET / UPDATE DECISION RATIONALE
@router.put(
    "/{decision_id}/rationale",
    response_model=DecisionRationaleResponse
)
def update_decision_rationale(
    decision_id: int,
    data: DecisionRationaleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = get_decision_or_404(decision_id, db)

    decision.rationale = data.rationale
    decision.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(decision)

    return DecisionRationaleResponse(
        decision_id=decision.id,
        rationale=decision.rationale
    )


# Sprint 7: GET DECISION RATIONALE
@router.get(
    "/{decision_id}/rationale",
    response_model=DecisionRationaleResponse
)
def get_decision_rationale(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = get_decision_or_404(decision_id, db)

    return DecisionRationaleResponse(
        decision_id=decision.id,
        rationale=decision.rationale
    )


# ---------------------------------------------------------------------
# Sprint 9: Tag management on a Decision
# ---------------------------------------------------------------------

# ASSIGN TAGS TO A DECISION
@router.post(
    "/{decision_id}/tags",
    response_model=list[TagResponse]
)
def assign_tags_to_decision(
    decision_id: int,
    payload: TagAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = get_decision_or_404(decision_id, db)

    tags = db.query(Tag).filter(Tag.id.in_(payload.tag_ids)).all()

    found_ids = {t.id for t in tags}
    missing_ids = set(payload.tag_ids) - found_ids

    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag id(s) not found: {sorted(missing_ids)}"
        )

    existing_ids = {t.id for t in decision.tags}

    for tag in tags:
        if tag.id not in existing_ids:
            decision.tags.append(tag)

    db.commit()
    db.refresh(decision)

    return decision.tags


# GET TAGS FOR A DECISION
@router.get(
    "/{decision_id}/tags",
    response_model=list[TagResponse]
)
def get_decision_tags(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = get_decision_or_404(decision_id, db)
    return decision.tags


# REMOVE A TAG FROM A DECISION
@router.delete(
    "/{decision_id}/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_tag_from_decision(
    decision_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = get_decision_or_404(decision_id, db)

    tag = next((t for t in decision.tags if t.id == tag_id), None)

    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag is not associated with this decision"
        )

    decision.tags.remove(tag)
    db.commit()

    return None


# ---------------------------------------------------------------------
# Sprint 9: Decision Timeline
# ---------------------------------------------------------------------

@router.get(
    "/{decision_id}/timeline",
    response_model=DecisionTimelineResponse
)
def get_decision_timeline(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = get_decision_or_404(decision_id, db)

    events = [
        {
            "event_type": "Decision created",
            "description": f"Decision '{decision.title}' was created",
            "timestamp": decision.created_at,
        }
    ]

    for alt in decision.alternatives:
        events.append({
            "event_type": "Alternative created",
            "description": f"Alternative '{alt.name}' was added",
            "timestamp": alt.created_at,
        })

    for thread in decision.threads:
        events.append({
            "event_type": "Discussion thread created",
            "description": f"Discussion thread '{thread.title}' was started",
            "timestamp": thread.created_at,
        })

    for comment in decision.comments:
        events.append({
            "event_type": "Comment added",
            "description": "A comment was added to the decision",
            "timestamp": comment.created_at,
        })

    for note in decision.meeting_notes:
        events.append({
            "event_type": "Meeting note added",
            "description": f"Meeting note '{note.title}' was added",
            "timestamp": note.created_at,
        })

    terminal_statuses = {
        DecisionStatus.APPROVED.value,
        DecisionStatus.REJECTED.value,
        DecisionStatus.ARCHIVED.value,
    }

    if decision.status in terminal_statuses:
        events.append({
            "event_type": f"Decision {decision.status.lower()}",
            "description": f"Decision status changed to {decision.status}",
            "timestamp": decision.updated_at,
        })
    elif decision.updated_at != decision.created_at:
        events.append({
            "event_type": "Decision updated",
            "description": "Decision details were updated",
            "timestamp": decision.updated_at,
        })

    events.sort(key=lambda e: e["timestamp"])

    return DecisionTimelineResponse(
        decision_id=decision.id,
        timeline=events
    )
