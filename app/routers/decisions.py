from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.database import get_db

from app.models.decision import Decision
from app.models.audit_log import AuditLog
from app.models.decision_version import DecisionVersion

from app.schemas.decision import (
    DecisionCreate,
    DecisionResponse,
    DecisionUpdate,
    DecisionStatusUpdate,
)

from app.core.security import get_current_user
from app.services.audit import create_audit_log
from app.services.access import create_access_log


router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)


# ============================================================
# CREATE DECISION
# POST /decisions
# ============================================================

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

    new_decision = Decision(
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status="Draft",
        created_by=current_user.id
    )

    db.add(new_decision)
    db.flush()

    # --------------------------------------------------------
    # CREATE INITIAL VERSION
    # --------------------------------------------------------

    version = DecisionVersion(
        decision_id=new_decision.id,
        version_number=1,
        title=new_decision.title,
        problem_statement=new_decision.problem_statement,
        category=new_decision.category,
        status=new_decision.status,
        created_by=current_user.id
    )

    db.add(version)

    # --------------------------------------------------------
    # AUDIT LOG
    # --------------------------------------------------------

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Decision",
        entity_id=new_decision.id,
        description=(
            f"User {current_user.id} created "
            f"Decision {new_decision.id}"
        ),
        new_value={
            "title": new_decision.title,
            "problem_statement": new_decision.problem_statement,
            "category": new_decision.category,
            "status": new_decision.status
        }
    )

    db.commit()
    db.refresh(new_decision)

    return new_decision


# ============================================================
# GET ALL DECISIONS
# GET /decisions
# ============================================================

@router.get(
    "",
    response_model=List[DecisionResponse]
)
def get_decisions(
    search: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    query = db.query(Decision)

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    if search:
        search_pattern = f"%{search}%"

        query = query.filter(
            or_(
                Decision.title.ilike(search_pattern),
                Decision.problem_statement.ilike(search_pattern)
            )
        )

    # --------------------------------------------------------
    # STATUS FILTER
    # --------------------------------------------------------

    if status:
        query = query.filter(
            Decision.status == status
        )

    # --------------------------------------------------------
    # CATEGORY FILTER
    # --------------------------------------------------------

    if category:
        query = query.filter(
            Decision.category == category
        )

    # --------------------------------------------------------
    # TAG FILTER
    # --------------------------------------------------------

    if tag:
        query = query.filter(
            Decision.tags.any(name=tag)
        )

    # --------------------------------------------------------
    # PAGINATION VALIDATION
    # --------------------------------------------------------

    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be greater than 0"
        )

    if limit < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be greater than 0"
        )

    # --------------------------------------------------------
    # SORTING
    # --------------------------------------------------------

    allowed_sort_fields = {
        "created_at": Decision.created_at,
        "updated_at": Decision.updated_at,
        "title": Decision.title,
        "status": Decision.status,
        "category": Decision.category,
    }

    sort_column = allowed_sort_fields.get(sort_by)

    if not sort_column:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sort field"
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
            detail="sort_order must be 'asc' or 'desc'"
        )

    # --------------------------------------------------------
    # PAGINATION
    # --------------------------------------------------------

    offset = (page - 1) * limit

    query = (
        query
        .offset(offset)
        .limit(limit)
    )

    return query.all()


# ============================================================
# GET DECISION BY ID
# GET /decisions/{decision_id}
# ============================================================

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
        .filter(
            Decision.id == decision_id
        )
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    # --------------------------------------------------------
    # ACCESS LOG
    # --------------------------------------------------------

    create_access_log(
        db=db,
        user_id=current_user.id,
        resource_type="Decision",
        resource_id=decision.id,
        action="VIEW"
    )

    db.commit()

    return decision


# ============================================================
# UPDATE DECISION
# PUT /decisions/{decision_id}
# ============================================================

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
        .filter(
            Decision.id == decision_id
        )
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    # --------------------------------------------------------
    # SAVE OLD VALUES
    # --------------------------------------------------------

    old_value = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category,
        "status": decision.status
    }

    # --------------------------------------------------------
    # UPDATE DECISION
    # --------------------------------------------------------

    decision.title = decision_data.title
    decision.problem_statement = decision_data.problem_statement
    decision.category = decision_data.category

    # --------------------------------------------------------
    # FIND LATEST VERSION
    # --------------------------------------------------------

    latest_version = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision.id
        )
        .order_by(
            DecisionVersion.version_number.desc()
        )
        .first()
    )

    if latest_version:
        next_version_number = (
            latest_version.version_number + 1
        )
    else:
        next_version_number = 1

    # --------------------------------------------------------
    # CREATE NEW VERSION
    # --------------------------------------------------------

    new_version = DecisionVersion(
        decision_id=decision.id,
        version_number=next_version_number,
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status=decision.status,
        created_by=current_user.id
    )

    db.add(new_version)

    # --------------------------------------------------------
    # NEW VALUES
    # --------------------------------------------------------

    new_value = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category,
        "status": decision.status
    }

    # --------------------------------------------------------
    # AUDIT LOG
    # --------------------------------------------------------

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"User {current_user.id} updated "
            f"Decision {decision.id}"
        ),
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

    decision = (
        db.query(Decision)
        .filter(
            Decision.id == decision_id
        )
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    old_status = decision.status

    decision.status = status_data.status.value

    # --------------------------------------------------------
    # FIND LATEST VERSION
    # --------------------------------------------------------

    latest_version = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision.id
        )
        .order_by(
            DecisionVersion.version_number.desc()
        )
        .first()
    )

    if latest_version:
        next_version_number = (
            latest_version.version_number + 1
        )
    else:
        next_version_number = 1

    # --------------------------------------------------------
    # CREATE VERSION
    # --------------------------------------------------------

    new_version = DecisionVersion(
        decision_id=decision.id,
        version_number=next_version_number,
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status=decision.status,
        created_by=current_user.id
    )

    db.add(new_version)

    # --------------------------------------------------------
    # AUDIT LOG
    # --------------------------------------------------------

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="STATUS_CHANGE",
        entity_type="Decision",
        entity_id=decision.id,
        description=(
            f"User {current_user.id} changed "
            f"Decision {decision.id} status from "
            f"{old_status} to {decision.status}"
        ),
        old_value={
            "status": old_status
        },
        new_value={
            "status": decision.status
        }
    )

    db.commit()
    db.refresh(decision)

    return decision


# ============================================================
# GET ALL DECISION VERSIONS
# GET /decisions/{decision_id}/versions
# ============================================================

@router.get(
    "/{decision_id}/versions"
)
def get_decision_versions(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    decision = (
        db.query(Decision)
        .filter(
            Decision.id == decision_id
        )
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
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
# GET /decisions/{decision_id}/versions/{version_number}
# ============================================================

@router.get(
    "/{decision_id}/versions/{version_number}"
)
def get_decision_version(
    decision_id: int,
    version_number: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if version_number < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid version number"
        )

    version = (
        db.query(DecisionVersion)
        .filter(
            DecisionVersion.decision_id == decision_id,
            DecisionVersion.version_number == version_number
        )
        .first()
    )

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision version not found"
        )

    return version


# ============================================================
# DECISION HISTORY
# GET /decisions/{decision_id}/history
# ============================================================

@router.get(
    "/{decision_id}/history"
)
def get_decision_history(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    decision = (
        db.query(Decision)
        .filter(
            Decision.id == decision_id
        )
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    history = (
        db.query(AuditLog)
        .filter(
            AuditLog.entity_type == "Decision",
            AuditLog.entity_id == decision_id
        )
        .order_by(
            AuditLog.created_at.asc()
        )
        .all()
    )

    return [
        {
            "id": item.id,
            "user_id": item.user_id,
            "action": item.action,
            "entity_type": item.entity_type,
            "entity_id": item.entity_id,
            "description": item.description,
            "old_value": item.old_value,
            "new_value": item.new_value,
            "created_at": item.created_at
        }
        for item in history
    ]