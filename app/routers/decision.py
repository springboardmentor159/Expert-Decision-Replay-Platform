from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db

from app.models.user import User
from app.models.decision import Decision

from app.models.tag import Tag


from app.schemas.tag import TagAssignment, TagResponse
from app.schemas.decision import (
    DecisionCreate,
    DecisionUpdate,
    DecisionResponse,
    DecisionListResponse,
    DecisionListItem,
)
from app.services.activity_service import log_activity

router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)


@router.post(
    "",
    response_model=DecisionResponse,
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
        category=decision_data.category,
        rationale=decision_data.rationale,
        status="Draft",
        created_by=current_user.id
    )

    db.add(new_decision)
    db.flush()

    log_activity(
        db,
        user_id=current_user.id,
        action="decision_created",
        entity_type="decision",
        entity_id=new_decision.id,
        description=f"User {current_user.id} created Decision {new_decision.id}"
    )

    db.commit()
    db.refresh(new_decision)

    return new_decision


@router.get(
    "",
    response_model=List[DecisionResponse]
)
def get_decisions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decisions = (
        db.query(Decision)
        .filter(Decision.created_by == current_user.id)
        .order_by(Decision.created_at.desc())
        .all()
    )
    return decisions


@router.get(
    "/search",
    response_model=DecisionListResponse
)
def search_decisions(
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort: str = Query("created_at"),
    order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Decision)

    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Decision.title.ilike(search_term),
                Decision.problem_statement.ilike(search_term),
                Decision.rationale.ilike(search_term)
            )
        )

    if category:
        query = query.filter(Decision.category == category)

    if tag:
        query = query.filter(Decision.tags.any(name=tag))

    allowed_sort_fields = {
        "created_at": Decision.created_at,
        "updated_at": Decision.updated_at,
        "title": Decision.title,
    }

    if sort not in allowed_sort_fields:
        raise HTTPException(status_code=422, detail="Invalid sort field")

    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=422, detail="Order must be 'asc' or 'desc'")

    sort_column = allowed_sort_fields[sort]
    query = query.order_by(
        sort_column.asc() if order == "asc" else sort_column.desc()
    )

    total = query.count()
    decisions = query.offset((page - 1) * page_size).limit(page_size).all()
    items = [DecisionListItem.model_validate(d) for d in decisions]

    return DecisionListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )


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

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return decision


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

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    if decision.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this decision"
        )

    if decision_data.title is not None:
        decision.title = decision_data.title
    if decision_data.problem_statement is not None:
        decision.problem_statement = decision_data.problem_statement
    if decision_data.category is not None:
        decision.category = decision_data.category
    if decision_data.rationale is not None:
        decision.rationale = decision_data.rationale

    log_activity(
        db,
        user_id=current_user.id,
        action="decision_updated",
        entity_type="decision",
        entity_id=decision.id,
        description=f"User {current_user.id} updated Decision {decision.id}"
    )

    db.commit()
    db.refresh(decision)

    return decision


    "/{decision_id}/submit",
    response_model=DecisionResponse

def submit_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    if decision.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to submit this decision"
        )

    if decision.status != "Draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Draft decisions can be submitted"
        )

    decision.status = "Under Review"

    log_activity(
        db,
        user_id=current_user.id,
        action="decision_submitted",
        entity_type="decision",
        entity_id=decision.id,
        description=f"User {current_user.id} submitted Decision {decision.id} for review"
    )

    db.commit()
    db.refresh(decision)

    return decision


@router.delete(
    "/{decision_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    if decision.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this decision"
        )

    db.delete(decision)
    db.commit()

    return None


@router.post(
    "/{decision_id}/tags",
    response_model=List[TagResponse]
)
def assign_tags_to_decision(
    decision_id: int,
    tag_data: TagAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    tags = db.query(Tag).filter(Tag.id.in_(tag_data.tag_ids)).all()
    found_tag_ids = {tag.id for tag in tags}
    missing_tag_ids = set(tag_data.tag_ids) - found_tag_ids

    if missing_tag_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag(s) not found: {sorted(missing_tag_ids)}"
        )

    existing_tag_ids = {tag.id for tag in decision.tags}
    for tag in tags:
        if tag.id not in existing_tag_ids:
            decision.tags.append(tag)

    db.commit()
    db.refresh(decision)

    return decision.tags


