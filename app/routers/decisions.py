from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.decision import Decision
from app.models.decision_version import DecisionVersion
from app.models.user import User
from app.schemas.audit_log import AuditAction, AuditEntityType
from app.schemas.decision import (
    DecisionCreate,
    DecisionResponse,
    DecisionStatusUpdate,
    DecisionUpdate,
)
from app.services.audit_service import log_audit


router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"]
)


# CREATE DECISION
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
    decision = Decision(
        title=decision_data.title,
        problem_statement=decision_data.problem_statement,
        category=decision_data.category,
        status="Draft",
        created_by=current_user.id
    )

    db.add(decision)
    db.flush()

    log_audit(
        db=db,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type=AuditEntityType.DECISION,
        entity_id=decision.id,
        description=f"Decision '{decision.title}' created",
        request_method="POST",
        endpoint="/decisions"
    )

    db.commit()
    db.refresh(decision)

    return decision


# GET ALL / FILTER DECISIONS
@router.get(
    "",
    response_model=List[DecisionResponse]
)
def get_decisions(
    status_filter: Optional[str] = Query(
        default=None,
        alias="status"
    ),
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Decision)

    if status_filter:
        query = query.filter(
            Decision.status == status_filter
        )

    if category:
        query = query.filter(
            Decision.category == category
        )

    return query.all()


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
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return decision


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
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    old_values = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category,
        "status": decision.status
    }

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

    next_version_number = (
        latest_version.version_number + 1
        if latest_version
        else 1
    )

    version = DecisionVersion(
        decision_id=decision.id,
        version_number=next_version_number,
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status=decision.status,
        changed_by=current_user.id,
        change_summary="Decision updated"
    )

    db.add(version)

    decision.title = decision_data.title
    decision.problem_statement = decision_data.problem_statement
    decision.category = decision_data.category

    new_values = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category,
        "status": decision.status
    }

    log_audit(
        db=db,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type=AuditEntityType.DECISION,
        entity_id=decision.id,
        description=f"Decision '{decision.title}' updated",
        old_value=old_values,
        new_value=new_values,
        request_method="PUT",
        endpoint=f"/decisions/{decision.id}"
    )

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
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    old_status = decision.status

    decision.status = status_data.status.value

    log_audit(
        db=db,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type=AuditEntityType.DECISION,
        entity_id=decision.id,
        description=(
            f"Decision status changed from "
            f"'{old_status}' to '{decision.status}'"
        ),
        old_value={
            "status": old_status
        },
        new_value={
            "status": decision.status
        },
        request_method="PATCH",
        endpoint=f"/decisions/{decision.id}/status"
    )

    db.commit()
    db.refresh(decision)

    return decision


# GET DECISION VERSION HISTORY
@router.get(
    "/{decision_id}/history"
)
def get_decision_history(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

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

    return [
        {
            "id": version.id,
            "decision_id": version.decision_id,
            "version_number": version.version_number,
            "title": version.title,
            "problem_statement": version.problem_statement,
            "category": version.category,
            "status": version.status,
            "changed_by": version.changed_by,
            "change_summary": version.change_summary,
            "created_at": version.created_at
        }
        for version in versions
    ]


# COMPARE DECISION VERSIONS
@router.get(
    "/{decision_id}/versions/compare"
)
def compare_decision_versions(
    decision_id: int,
    version_a: int,
    version_b: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    first_version = db.query(DecisionVersion).filter(
        DecisionVersion.decision_id == decision_id,
        DecisionVersion.version_number == version_a
    ).first()

    second_version = db.query(DecisionVersion).filter(
        DecisionVersion.decision_id == decision_id,
        DecisionVersion.version_number == version_b
    ).first()

    if not first_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_a} not found"
        )

    if not second_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_b} not found"
        )

    differences = {}

    if first_version.title != second_version.title:
        differences["title"] = {
            "version_a": first_version.title,
            "version_b": second_version.title
        }

    if first_version.problem_statement != second_version.problem_statement:
        differences["problem_statement"] = {
            "version_a": first_version.problem_statement,
            "version_b": second_version.problem_statement
        }

    if first_version.category != second_version.category:
        differences["category"] = {
            "version_a": first_version.category,
            "version_b": second_version.category
        }

    if first_version.status != second_version.status:
        differences["status"] = {
            "version_a": first_version.status,
            "version_b": second_version.status
        }

    return {
        "decision_id": decision_id,
        "version_a": version_a,
        "version_b": version_b,
        "differences": differences
    }


# GET SPECIFIC DECISION VERSION
@router.get(
    "/{decision_id}/versions/{version_number}"
)
def get_decision_version(
    decision_id: int,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    version = db.query(DecisionVersion).filter(
        DecisionVersion.decision_id == decision_id,
        DecisionVersion.version_number == version_number
    ).first()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision version not found"
        )

    return {
        "id": version.id,
        "decision_id": version.decision_id,
        "version_number": version.version_number,
        "title": version.title,
        "problem_statement": version.problem_statement,
        "category": version.category,
        "status": version.status,
        "changed_by": version.changed_by,
        "change_summary": version.change_summary,
        "created_at": version.created_at
    }