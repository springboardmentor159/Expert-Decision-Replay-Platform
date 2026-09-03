from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.database import get_db
from app.models.decision import Decision
from app.models.user import User
from app.models.tag import Tag
from app.routers.auth import get_current_user
from app.services.audit_service import create_audit_log
from app.models.audit_log import AuditLog

from app.schemas.decision import (
    DecisionCreate,
    DecisionUpdate,
    DecisionResponse,
    DecisionStatus,
    DecisionStatusUpdate,
    DecisionRationaleUpdate
)

from app.schemas.tag import DecisionTagRequest, TagResponse


router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)


# ============================================================
# CREATE DECISION
# POST /decisions/
# ============================================================

@router.post("/", response_model=DecisionResponse)
def create_decision(
    decision: DecisionCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_decision = Decision(
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status="Draft",
        created_by=current_user.id
    )

    db.add(new_decision)
    db.commit()
    db.refresh(new_decision)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Decision",
        entity_id=new_decision.id,
        description="Decision created",
        request_method="POST",
        endpoint="/decisions/"
    )

    db.commit()

    return new_decision
      
    


# ============================================================
# GET DECISIONS
# GET /decisions/
#
# Supports:
# category
# status
# tag
# page
# page_size
# sort
# order
# ============================================================

@router.get("/")
def get_all_decisions(
    status: DecisionStatus | None = Query(default=None),
    category: str | None = Query(default=None),
    tag: str | None = Query(default=None),

    page: int = Query(
        default=1,
        ge=1
    ),

    page_size: int = Query(
        default=10,
        ge=1,
        le=100
    ),

    sort: str = Query(
        default="created_at"
    ),

    order: str = Query(
        default="desc"
    ),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    allowed_sort_fields = {
        "created_at": Decision.created_at,
        "updated_at": Decision.updated_at,
        "title": Decision.title
    }

    if sort not in allowed_sort_fields:
        raise HTTPException(
            status_code=422,
            detail=(
                "Invalid sort field. Allowed values: "
                "created_at, updated_at, title"
            )
        )

    if order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=422,
            detail="Invalid order. Allowed values: asc, desc"
        )

    query = db.query(Decision)

    # Status filter
    if status is not None:
        query = query.filter(
            Decision.status == status.value
        )

    # Category filter
    if category is not None:
        query = query.filter(
            Decision.category == category
        )

    # Tag filter
    if tag is not None:
        query = query.join(
            Decision.tags
        ).filter(
            Tag.name == tag
        )

    # Remove duplicate decisions caused by joins
    query = query.distinct()

    # Sorting
    sort_column = allowed_sort_fields[sort]

    if order == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    # Total count before pagination
    total = query.count()

    # Pagination
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
        "total": total
    }


# ============================================================
# SEARCH DECISIONS
# GET /decisions/search
#
# Supports:
# q
# category
# status
# tag
# page
# page_size
# sort
# order
# ============================================================

@router.get("/search")
def search_decisions(
    q: str | None = Query(default=None),
    status: DecisionStatus | None = Query(default=None),
    category: str | None = Query(default=None),
    tag: str | None = Query(default=None),

    page: int = Query(
        default=1,
        ge=1
    ),

    page_size: int = Query(
        default=10,
        ge=1,
        le=100
    ),

    sort: str = Query(
        default="created_at"
    ),

    order: str = Query(
        default="desc"
    ),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Search parameter validation
    if q is not None:
        q = q.strip()

        if not q:
            raise HTTPException(
                status_code=422,
                detail="Search keyword cannot be empty"
            )

    allowed_sort_fields = {
        "created_at": Decision.created_at,
        "updated_at": Decision.updated_at,
        "title": Decision.title
    }

    if sort not in allowed_sort_fields:
        raise HTTPException(
            status_code=422,
            detail=(
                "Invalid sort field. Allowed values: "
                "created_at, updated_at, title"
            )
        )

    if order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=422,
            detail="Invalid order. Allowed values: asc, desc"
        )

    query = db.query(Decision)

    # Keyword search
    if q is not None:
        keyword = f"%{q}%"

        query = query.filter(
            or_(
                Decision.title.ilike(keyword),
                Decision.problem_statement.ilike(keyword),
                Decision.rationale.ilike(keyword)
            )
        )

    # Status filter
    if status is not None:
        query = query.filter(
            Decision.status == status.value
        )

    # Category filter
    if category is not None:
        query = query.filter(
            Decision.category == category
        )

    # Tag filter
    if tag is not None:
        query = query.join(
            Decision.tags
        ).filter(
            Tag.name == tag
        )

    # Remove duplicates
    query = query.distinct()

    # Sorting
    sort_column = allowed_sort_fields[sort]

    if order == "asc":
        query = query.order_by(
            sort_column.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc()
        )

    # Count
    total = query.count()

    # Pagination
    offset = (page - 1) * page_size

    results = query.offset(
        offset
    ).limit(
        page_size
    ).all()

    return {
        "items": results,
        "page": page,
        "page_size": page_size,
        "total": total
    }


# ============================================================
# GET DECISION BY ID
# GET /decisions/{decision_id}
# ============================================================

@router.get("/{decision_id}", response_model=DecisionResponse)
def get_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    return decision


# ============================================================
# UPDATE DECISION
# PUT /decisions/{decision_id}
# ============================================================

@router.put("/{decision_id}", response_model=DecisionResponse)
def update_decision(
    decision_id: int,
    decision_data: DecisionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    if decision.status == "Archived":
        raise HTTPException(
            status_code=403,
            detail="Archived decisions cannot be modified"
        )

    # Save old values before updating
    old_value = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category
    }

    if decision_data.title is not None:
        decision.title = decision_data.title

    if decision_data.problem_statement is not None:
        decision.problem_statement = decision_data.problem_statement

    if decision_data.category is not None:
        decision.category = decision_data.category

    # Save new values after updating
    new_value = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category
    }

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Decision",
        entity_id=decision.id,
        description="Decision updated",
        request_method="PUT",
        endpoint=f"/decisions/{decision.id}",
        old_value=old_value,
        new_value=new_value
    )

    db.commit()
    db.refresh(decision)

    return decision


# ============================================================
# UPDATE DECISION STATUS
# PATCH /decisions/{decision_id}/status
# ============================================================

@router.patch("/{decision_id}/status", response_model=DecisionResponse)
def update_decision_status(
    decision_id: int,
    status_data: DecisionStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    if decision.status == "Archived":
        raise HTTPException(
            status_code=403,
            detail="Archived decisions cannot be modified"
        )

    decision.status = status_data.status.value

    db.commit()
    db.refresh(decision)

    return decision


# ============================================================
# DELETE DECISION
# DELETE /decisions/{decision_id}
# ============================================================


@router.delete("/{decision_id}")
def delete_decision(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    old_value = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category,
        "status": decision.status,
        "created_by": decision.created_by
    }

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="Decision",
        entity_id=decision.id,
        description="Decision deleted",
        request_method="DELETE",
        endpoint=f"/decisions/{decision.id}",
        old_value=old_value,
        new_value=None
    )

    db.delete(decision)
    db.commit()

    return {
        "message": "Decision deleted successfully"
    }


# ============================================================
# UPDATE DECISION RATIONALE
# PUT /decisions/{decision_id}/rationale
# ============================================================

@router.put("/{decision_id}/rationale")
def update_decision_rationale(
    decision_id: int,
    rationale_data: DecisionRationaleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    if decision.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to update this decision rationale"
        )

    if decision.status == "Archived":
        raise HTTPException(
            status_code=403,
            detail="Archived decisions cannot be modified"
        )

    decision.rationale = rationale_data.rationale

    db.commit()
    db.refresh(decision)

    return {
        "message": "Decision rationale updated successfully",
        "decision_id": decision.id,
        "rationale": decision.rationale
    }


# ============================================================
# GET DECISION RATIONALE
# GET /decisions/{decision_id}/rationale
# ============================================================

@router.get("/{decision_id}/rationale")
def get_decision_rationale(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    return {
        "decision_id": decision.id,
        "rationale": decision.rationale
    }


# ============================================================
# ADD TAGS TO DECISION
# POST /decisions/{decision_id}/tags
# ============================================================

@router.post("/{decision_id}/tags")
def add_tags_to_decision(
    decision_id: int,
    tag_data: DecisionTagRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    tags = db.query(Tag).filter(
        Tag.id.in_(tag_data.tag_ids)
    ).all()

    found_tag_ids = {tag.id for tag in tags}
    requested_tag_ids = set(tag_data.tag_ids)

    missing_tag_ids = requested_tag_ids - found_tag_ids

    if missing_tag_ids:
        raise HTTPException(
            status_code=404,
            detail=f"Tag(s) not found: {list(missing_tag_ids)}"
        )

    for tag in tags:
        if tag not in decision.tags:
            decision.tags.append(tag)

    db.commit()
    db.refresh(decision)

    return {
        "message": "Tags added to decision successfully",
        "decision_id": decision.id,
        "tag_ids": [tag.id for tag in decision.tags]
    }


# ============================================================
# GET TAGS OF A DECISION
# GET /decisions/{decision_id}/tags
# ============================================================

@router.get(
    "/{decision_id}/tags",
    response_model=list[TagResponse]
)
def get_decision_tags(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    return decision.tags


# ============================================================
# REMOVE TAG FROM DECISION
# DELETE /decisions/{decision_id}/tags/{tag_id}
# ============================================================

@router.delete(
    "/{decision_id}/tags/{tag_id}"
)
def remove_tag_from_decision(
    decision_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    tag = db.query(Tag).filter(
        Tag.id == tag_id
    ).first()

    if not tag:
        raise HTTPException(
            status_code=404,
            detail="Tag not found"
        )

    if tag not in decision.tags:
        raise HTTPException(
            status_code=404,
            detail="Tag is not assigned to this decision"
        )

    decision.tags.remove(tag)

    db.commit()

    return {
        "message": "Tag removed from decision successfully",
        "decision_id": decision_id,
        "tag_id": tag_id
    }
# ============================================================
# GET DECISION TIMELINE
# GET /decisions/{decision_id}/timeline
# ============================================================

@router.get("/{decision_id}/timeline")
def get_decision_timeline(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    audit_logs = db.query(AuditLog).filter(
        AuditLog.entity_type == "Decision",
        AuditLog.entity_id == decision_id
    ).order_by(
        AuditLog.created_at.asc()
    ).all()

    timeline = []

    for log in audit_logs:
        timeline.append({
            "event_type": log.action,
            "description": log.description,
            "user_id": log.user_id,
            "created_at": log.created_at
        })

    return {
        "decision_id": decision_id,
        "timeline": timeline
    }