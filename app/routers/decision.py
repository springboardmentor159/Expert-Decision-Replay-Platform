from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.decision import Decision
from app.models.decision_version import DecisionVersion
from app.models.enums import DecisionStatus, UserRole
from app.models.user import User
from app.services.activity import log_activity
from app.services.audit import log_audit
from app.schemas.decision import (
    DecisionCreate,
    DecisionHistoryResponse,
    DecisionRationaleUpdate,
    DecisionResponse,
    DecisionStatusUpdate,
    DecisionUpdate,
    DecisionVersionListResponse,
)
from app.schemas.decision_version import DecisionVersionResponse

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
    request: Request,
    decision_data: DecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_decision = Decision(
        title=decision_data.title,
        problem_statement=decision_data.problem_statement,
        category=decision_data.category,
        status="Draft",
        created_by=current_user.id
    )

    db.add(new_decision)
    db.commit()
    db.refresh(new_decision)

    version = DecisionVersion(
        decision_id=new_decision.id,
        version_number=1,
        title=new_decision.title,
        problem_statement=new_decision.problem_statement,
        category=new_decision.category,
        status=new_decision.status.value if isinstance(new_decision.status, DecisionStatus) else new_decision.status,
        rationale=new_decision.rationale,
        created_by=new_decision.created_by,
    )
    db.add(version)
    db.commit()

    log_activity(
        db,
        current_user.id,
        "create",
        "decision",
        new_decision.id,
        f"Created decision '{new_decision.title}'",
    )

    log_audit(
        db,
        current_user.id,
        "create",
        "decision",
        new_decision.id,
        f"Created decision '{new_decision.title}'",
        ip_address=request.client.host if request.client else None,
    )

    return new_decision


@router.get(
    "",
    response_model=List[DecisionResponse]
)
def get_decisions(
    status: Optional[DecisionStatus] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Decision)

    if status is not None:
        query = query.filter(Decision.status == status.value)

    if category is not None:
        query = query.filter(Decision.category == category)

    decisions = query.all()
    return decisions


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


@router.put(
    "/{decision_id}",
    response_model=DecisionResponse
)
def update_decision(
    request: Request,
    decision_id: int,
    decision_data: DecisionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    old_values = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category,
        "status": decision.status.value if isinstance(decision.status, DecisionStatus) else decision.status,
        "rationale": decision.rationale,
    }

    if decision_data.title is not None:
        decision.title = decision_data.title

    if decision_data.problem_statement is not None:
        decision.problem_statement = decision_data.problem_statement

    if decision_data.category is not None:
        decision.category = decision_data.category

    decision.updated_at = func.now()

    db.commit()
    db.refresh(decision)

    new_values = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category,
        "status": decision.status.value if isinstance(decision.status, DecisionStatus) else decision.status,
        "rationale": decision.rationale,
    }

    version = DecisionVersion(
        decision_id=decision.id,
        version_number=_get_next_version_number(db, decision.id),
        title=old_values["title"],
        problem_statement=old_values["problem_statement"],
        category=old_values["category"],
        status=old_values["status"],
        rationale=old_values.get("rationale"),
        created_by=decision.created_by,
    )
    db.add(version)
    db.commit()

    log_activity(
        db,
        current_user.id,
        "update",
        "decision",
        decision.id,
        f"Updated decision '{decision.title}'",
    )

    log_audit(
        db,
        current_user.id,
        "update",
        "decision",
        decision.id,
        f"Updated decision '{decision.title}'",
        old_values=old_values,
        new_values=new_values,
        ip_address=request.client.host if request.client else None,
    )

    return decision


@router.patch(
    "/{decision_id}/status",
    response_model=DecisionResponse
)
def update_decision_status(
    request: Request,
    decision_id: int,
    status_data: DecisionStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    old_status = decision.status.value if isinstance(decision.status, DecisionStatus) else decision.status
    decision.status = status_data.status
    decision.updated_at = func.now()

    db.commit()
    db.refresh(decision)

    version = DecisionVersion(
        decision_id=decision.id,
        version_number=_get_next_version_number(db, decision.id),
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status=old_status,
        rationale=decision.rationale,
        created_by=decision.created_by,
    )
    db.add(version)
    db.commit()

    log_activity(
        db,
        current_user.id,
        "status_change",
        "decision",
        decision.id,
        f"Changed decision status from '{old_status}' to '{decision.status.value if isinstance(decision.status, DecisionStatus) else decision.status}'",
    )

    log_audit(
        db,
        current_user.id,
        "status_change",
        "decision",
        decision.id,
        f"Changed decision status from '{old_status}' to '{decision.status.value if isinstance(decision.status, DecisionStatus) else decision.status}'",
        old_values={"status": old_status},
        new_values={"status": decision.status.value if isinstance(decision.status, DecisionStatus) else decision.status},
        ip_address=request.client.host if request.client else None,
    )

    return decision


@router.put(
    "/{decision_id}/rationale",
    response_model=DecisionResponse
)
def update_decision_rationale(
    request: Request,
    decision_id: int,
    rationale_data: DecisionRationaleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    if decision.created_by != current_user.id and current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this decision rationale"
        )

    old_rationale = decision.rationale
    decision.rationale = rationale_data.rationale
    decision.updated_at = func.now()

    db.commit()
    db.refresh(decision)

    version = DecisionVersion(
        decision_id=decision.id,
        version_number=_get_next_version_number(db, decision.id),
        title=decision.title,
        problem_statement=decision.problem_statement,
        category=decision.category,
        status=decision.status.value if isinstance(decision.status, DecisionStatus) else decision.status,
        rationale=decision.rationale,
        created_by=decision.created_by,
    )
    db.add(version)
    db.commit()

    log_audit(
        db,
        current_user.id,
        "update",
        "decision",
        decision.id,
        f"Updated decision rationale",
        old_values={"rationale": old_rationale},
        new_values={"rationale": decision.rationale},
        ip_address=request.client.host if request.client else None,
    )

    return decision


@router.get(
    "/{decision_id}/versions",
    response_model=DecisionVersionListResponse
)
def get_decision_versions(
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

    versions = db.query(DecisionVersion).filter(
        DecisionVersion.decision_id == decision_id
    ).order_by(DecisionVersion.version_number.desc()).all()

    return DecisionVersionListResponse(versions=versions)


@router.get(
    "/{decision_id}/versions/{version_number}",
    response_model=DecisionVersionResponse
)
def get_decision_version(
    decision_id: int,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    version = db.query(DecisionVersion).filter(
        DecisionVersion.decision_id == decision_id,
        DecisionVersion.version_number == version_number
    ).first()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )

    return version


@router.get(
    "/{decision_id}/history",
    response_model=DecisionHistoryResponse
)
def get_decision_history(
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

    from app.models.audit_log import AuditLog

    history = db.query(AuditLog).filter(
        AuditLog.entity_type == "decision",
        AuditLog.entity_id == decision_id
    ).order_by(AuditLog.created_at.desc()).all()

    return DecisionHistoryResponse(items=history)


def _get_next_version_number(db: Session, decision_id: int) -> int:
    max_version = db.query(func.max(DecisionVersion.version_number)).filter(
        DecisionVersion.decision_id == decision_id
    ).scalar()
    return (max_version or 0) + 1
