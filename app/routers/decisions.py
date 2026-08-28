from datetime import datetime
from typing import Any, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.activity_log import ActivityLog
from app.models.alternative import Alternative
from app.models.approval import Approval
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.discussion_thread import DiscussionThread
from app.models.meeting_note import MeetingNote
from app.models.tag import Tag, decision_tags
from app.models.user import User
from app.schemas.decision import (
    DecisionCategory,
    DecisionCreate,
    DecisionRationaleResponse,
    DecisionRationaleUpdate,
    DecisionResponse,
    DecisionStatus,
    DecisionStatusUpdate,
    DecisionTimelineEvent,
    DecisionTimelineResponse,
    DecisionUpdate,
    PaginatedDecisionsResponse,
)
from app.schemas.tag import TagAssign, TagSimpleResponse
from app.services.activity_logger import log_activity

VALID_CATEGORIES = {
    "Technology",
    "Finance",
    "Operations",
    "Human Resources",
    "Security",
    "Product",
    "Infrastructure",
    "Strategy",
    "Architecture",
}

ALLOWED_SORT_FIELDS = {"created_at", "updated_at", "title", "status", "category"}

router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)


def _validate_category(category_name: str) -> str:
    """Validate category against controlled list or ensure non-empty normalized string"""
    if not category_name or not category_name.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Category cannot be empty"
        )
    cat_clean = category_name.strip()
    for valid in VALID_CATEGORIES:
        if valid.lower() == cat_clean.lower():
            return valid
    return cat_clean


# --- 1. DECISION SEARCH (Sprint 9) ---
@router.get(
    "/search",
    response_model=PaginatedDecisionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Search decisions with keyword, category, status, and tag filters"
)
def search_decisions(
    q: Optional[str] = Query(None, description="Search keyword in title, problem statement, rationale"),
    category: Optional[str] = Query(None, description="Category filter"),
    status_filter: Optional[str] = Query(None, alias="status", description="Status filter"),
    tag: Optional[str] = Query(None, description="Tag filter"),
    sort: Optional[str] = Query("created_at", description="Sort column (created_at, updated_at, title, category, status)"),
    order: Optional[str] = Query("desc", description="Sort order (asc, desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if sort not in ALLOWED_SORT_FIELDS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid sort field '{sort}'. Allowed: {', '.join(sorted(ALLOWED_SORT_FIELDS))}"
        )

    order_lower = order.lower() if order else "desc"
    if order_lower not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Order must be 'asc' or 'desc'"
        )

    query = db.query(Decision)

    if q and q.strip():
        term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Decision.title.ilike(term),
                Decision.problem_statement.ilike(term),
                Decision.rationale.ilike(term)
            )
        )

    if category and category.strip():
        query = query.filter(func.lower(Decision.category) == func.lower(category.strip()))

    if status_filter and status_filter.strip():
        valid_statuses = {s.value.lower(): s.value for s in DecisionStatus}
        if status_filter.strip().lower() not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid status '{status_filter}'. Allowed: {', '.join([s.value for s in DecisionStatus])}"
            )
        actual_status = valid_statuses[status_filter.strip().lower()]
        query = query.filter(Decision.status == actual_status)

    if tag and tag.strip():
        query = query.join(Decision.tags).filter(func.lower(Tag.name) == func.lower(tag.strip()))

    total = query.distinct().count()

    sort_col = getattr(Decision, sort)
    if order_lower == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    items = query.distinct().offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedDecisionsResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        results=items
    )


# --- 2. CREATE DECISION ---
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
    validated_cat = _validate_category(decision.category)

    new_decision = Decision(
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=validated_cat,
        status="Draft",
        created_by=current_user.id
    )
    db.add(new_decision)
    db.commit()
    db.refresh(new_decision)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="create_decision",
        entity_type="decision",
        entity_id=new_decision.id,
        description=f"User {current_user.full_name} created decision '{new_decision.title}' in category '{validated_cat}'"
    )

    return new_decision


# --- 3. GET DECISIONS (Supports List and Optional Pagination / Filtering) ---
@router.get(
    "",
    response_model=Union[PaginatedDecisionsResponse, List[DecisionResponse]]
)
def get_decisions(
    status_filter: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query("created_at"),
    order: Optional[str] = Query("desc"),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if sort and sort not in ALLOWED_SORT_FIELDS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid sort field '{sort}'. Allowed: {', '.join(sorted(ALLOWED_SORT_FIELDS))}"
        )

    order_lower = order.lower() if order else "desc"
    if order_lower not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Order must be 'asc' or 'desc'"
        )

    query = db.query(Decision)

    if q and q.strip():
        term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Decision.title.ilike(term),
                Decision.problem_statement.ilike(term),
                Decision.rationale.ilike(term)
            )
        )

    if status_filter and status_filter.strip():
        valid_statuses = {s.value.lower(): s.value for s in DecisionStatus}
        if status_filter.strip().lower() not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid status '{status_filter}'. Allowed: {', '.join([s.value for s in DecisionStatus])}"
            )
        actual_status = valid_statuses[status_filter.strip().lower()]
        query = query.filter(Decision.status == actual_status)

    if category and category.strip():
        query = query.filter(func.lower(Decision.category) == func.lower(category.strip()))

    if tag and tag.strip():
        query = query.join(Decision.tags).filter(func.lower(Tag.name) == func.lower(tag.strip()))

    sort_col = getattr(Decision, sort if sort else "created_at")
    if order_lower == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    if page is not None and page_size is not None:
        total = query.distinct().count()
        items = query.distinct().offset((page - 1) * page_size).limit(page_size).all()
        return PaginatedDecisionsResponse(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            results=items
        )

    return query.distinct().all()


# --- 4. GET DECISION BY ID ---
@router.get(
    "/{decision_id}",
    response_model=DecisionResponse
)
def get_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )
    return decision


# --- 5. UPDATE DECISION ---
@router.put(
    "/{decision_id}",
    response_model=DecisionResponse
)
def update_decision(
    decision_id: int,
    decision_update: DecisionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    if decision.status == "Archived" and current_user.role not in ["Administrator", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify an archived decision"
        )

    validated_cat = _validate_category(decision_update.category)

    decision.title = decision_update.title
    decision.problem_statement = decision_update.problem_statement
    decision.category = validated_cat

    db.commit()
    db.refresh(decision)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="update_decision",
        entity_type="decision",
        entity_id=decision.id,
        description=f"User {current_user.full_name} updated decision '{decision.title}'"
    )

    return decision


# --- 6. UPDATE DECISION STATUS ---
@router.patch(
    "/{decision_id}/status",
    response_model=DecisionResponse
)
def update_decision_status(
    decision_id: int,
    status_update: DecisionStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    old_status = decision.status
    new_status = status_update.status.value

    decision.status = new_status
    db.commit()
    db.refresh(decision)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="update_decision_status",
        entity_type="decision",
        entity_id=decision.id,
        description=f"User {current_user.full_name} changed decision status from '{old_status}' to '{new_status}'"
    )

    return decision


# --- 7. UPDATE DECISION RATIONALE ---
@router.put(
    "/{decision_id}/rationale",
    response_model=DecisionResponse,
    status_code=status.HTTP_200_OK,
    summary="Record or update decision rationale"
)
def update_decision_rationale(
    decision_id: int,
    rationale_update: DecisionRationaleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    if decision.created_by != current_user.id and current_user.role not in ["Administrator", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update rationale for this decision"
        )

    decision.rationale = rationale_update.rationale
    db.commit()
    db.refresh(decision)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="update_rationale",
        entity_type="decision",
        entity_id=decision.id,
        description=f"User {current_user.full_name} updated rationale for decision '{decision.title}'"
    )

    return decision


# --- 8. GET DECISION RATIONALE ---
@router.get(
    "/{decision_id}/rationale",
    response_model=DecisionRationaleResponse,
    status_code=status.HTTP_200_OK,
    summary="Get decision rationale"
)
def get_decision_rationale(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return DecisionRationaleResponse(
        decision_id=decision.id,
        rationale=decision.rationale
    )


# --- 9. ASSIGN TAGS TO DECISION ---
@router.post(
    "/{decision_id}/tags",
    response_model=List[TagSimpleResponse],
    status_code=status.HTTP_200_OK,
    summary="Assign tags to a decision"
)
def assign_tags_to_decision(
    decision_id: int,
    tag_in: TagAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    # Verify all tags exist
    tags = db.query(Tag).filter(Tag.id.in_(tag_in.tag_ids)).all()
    if len(tags) != len(set(tag_in.tag_ids)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more specified tags do not exist"
        )

    # Add tags without duplicates
    existing_tag_ids = {t.id for t in decision.tags}
    for tag in tags:
        if tag.id not in existing_tag_ids:
            decision.tags.append(tag)

    db.commit()
    db.refresh(decision)

    tag_names = ", ".join([t.name for t in tags])
    log_activity(
        db=db,
        user_id=current_user.id,
        action="assign_tags",
        entity_type="decision",
        entity_id=decision.id,
        description=f"User {current_user.full_name} assigned tags [{tag_names}] to decision '{decision.title}'"
    )

    return [TagSimpleResponse(id=t.id, name=t.name) for t in decision.tags]


# --- 10. GET DECISION TAGS ---
@router.get(
    "/{decision_id}/tags",
    response_model=List[TagSimpleResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all tags assigned to a decision"
)
def get_decision_tags(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return [TagSimpleResponse(id=t.id, name=t.name) for t in decision.tags]


# --- 11. REMOVE TAG FROM DECISION ---
@router.delete(
    "/{decision_id}/tags/{tag_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove a tag from a decision"
)
def remove_tag_from_decision(
    decision_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    tag_to_remove = None
    for t in decision.tags:
        if t.id == tag_id:
            tag_to_remove = t
            break

    if not tag_to_remove:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not associated with this decision"
        )

    decision.tags.remove(tag_to_remove)
    db.commit()

    log_activity(
        db=db,
        user_id=current_user.id,
        action="remove_tag",
        entity_type="decision",
        entity_id=decision.id,
        description=f"User {current_user.full_name} removed tag '{tag_to_remove.name}' from decision '{decision.title}'"
    )

    return {"message": f"Tag '{tag_to_remove.name}' removed from decision successfully"}


# --- 12. DECISION TIMELINE (Sprint 9) ---
@router.get(
    "/{decision_id}/timeline",
    response_model=DecisionTimelineResponse,
    status_code=status.HTTP_200_OK,
    summary="Get chronological timeline of events for a decision"
)
def get_decision_timeline(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    events: List[DecisionTimelineEvent] = []

    # 1. Decision Creation
    events.append(
        DecisionTimelineEvent(
            event_type="Decision created",
            description=f"Decision '{decision.title}' created in category '{decision.category}'",
            user_id=decision.created_by,
            user_name=decision.creator.full_name if decision.creator else None,
            timestamp=decision.created_at
        )
    )

    # 2. Alternatives
    for alt in decision.alternatives:
        events.append(
            DecisionTimelineEvent(
                id=alt.id,
                event_type="Alternative created",
                description=f"Alternative '{alt.name}' added (Risk: {alt.risk_level}, Feasibility: {alt.feasibility_score})",
                timestamp=alt.created_at
            )
        )

    # 3. Comments
    for com in decision.comments:
        events.append(
            DecisionTimelineEvent(
                id=com.id,
                event_type="Comment added",
                description=f"Comment added: {com.content[:60]}...",
                user_id=com.user_id,
                user_name=com.author.full_name if com.author else None,
                timestamp=com.created_at
            )
        )

    # 4. Discussion Threads
    for th in decision.threads:
        events.append(
            DecisionTimelineEvent(
                id=th.id,
                event_type="Discussion thread created",
                description=f"Discussion thread '{th.title}' opened",
                user_id=th.created_by,
                user_name=th.creator.full_name if th.creator else None,
                timestamp=th.created_at
            )
        )

    # 5. Meeting Notes
    for mn in decision.meeting_notes:
        events.append(
            DecisionTimelineEvent(
                id=mn.id,
                event_type="Meeting note added",
                description=f"Meeting note '{mn.title}' recorded",
                user_id=mn.created_by,
                user_name=mn.creator.full_name if mn.creator else None,
                timestamp=mn.meeting_date if mn.meeting_date else mn.created_at
            )
        )

    # 6. Approvals
    for apprv in decision.approvals:
        events.append(
            DecisionTimelineEvent(
                id=apprv.id,
                event_type="Approval assigned",
                description=f"Approval assigned to reviewer (Level {apprv.approval_level}, Status: {apprv.status})",
                user_id=apprv.reviewer_id,
                user_name=apprv.reviewer.full_name if apprv.reviewer else None,
                timestamp=apprv.created_at
            )
        )
        if apprv.completed_at:
            events.append(
                DecisionTimelineEvent(
                    id=apprv.id,
                    event_type=f"Decision {apprv.status.lower()}",
                    description=f"Decision {apprv.status} by reviewer: {apprv.comments or 'No comments'}",
                    user_id=apprv.reviewer_id,
                    user_name=apprv.reviewer.full_name if apprv.reviewer else None,
                    timestamp=apprv.completed_at
                )
            )

    # 7. Activity logs for this decision
    act_logs = db.query(ActivityLog).filter(
        ActivityLog.entity_type == "decision",
        ActivityLog.entity_id == decision_id
    ).all()
    logged_actions = {"update_decision", "update_decision_status", "update_rationale", "assign_tags", "remove_tag"}
    for al in act_logs:
        if al.action in logged_actions:
            events.append(
                DecisionTimelineEvent(
                    id=al.id,
                    event_type=al.action.replace("_", " ").title(),
                    description=al.description,
                    user_id=al.user_id,
                    user_name=al.user.full_name if al.user else None,
                    timestamp=al.created_at
                )
            )

    # Sort all events chronologically
    events.sort(key=lambda x: x.timestamp)

    return DecisionTimelineResponse(
        decision_id=decision.id,
        decision_title=decision.title,
        current_status=decision.status,
        events=events
    )
