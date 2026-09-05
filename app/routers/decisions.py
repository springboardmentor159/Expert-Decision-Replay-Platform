from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.models.decision import Decision
from app.models.alternative import Alternative
from app.models.tag import Tag
from app.models.approval import Approval
from app.models.decision_version import DecisionVersion

from app.schemas.decision import (
    DecisionCreate,
    DecisionResponse,
    DecisionUpdate,
    DecisionStatusUpdate,
    DecisionVersionResponse,
    DecisionVersionListResponse,
    DecisionHistoryResponse,
)

from app.schemas.alternative import (
    AlternativeCreate,
    AlternativeResponse,
)

from app.schemas.tag import (
    DecisionTagAssign,
    TagResponse,
)

from app.core.dependencies import get_current_user

from app.services.activity_log_service import create_activity_log
from app.services.audit_log_service import create_audit_log
from app.services.decision_version_service import create_decision_version
from app.services.access_log_service import create_access_log


router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"],
    dependencies=[Depends(get_current_user)]
)


# =========================================================
# SPRINT 11 - DECISION HISTORY RBAC
# =========================================================

def check_decision_history_access(
    db: Session,
    decision: Decision,
    current_user: dict
):
    user_id = int(current_user["sub"])
    role = current_user.get("role")

    # Administrator can access all decision history
    if role == "Administrator":
        return

    # Manager can access team decision history.
    # Current User model has no team-membership field,
    # so Manager access is currently organization-wide.
    if role == "Manager":
        return

    # Employee can access only decisions created by themselves
    if role == "Employee":
        if decision.created_by != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this decision history"
            )
        return

    # Reviewer can access decisions assigned to them
    if role == "Reviewer":
        assigned = (
            db.query(Approval)
            .filter(
                Approval.decision_id == decision.id,
                Approval.assigned_to == user_id
            )
            .first()
        )

        if not assigned:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this decision history"
            )

        return

    raise HTTPException(
        status_code=403,
        detail="You do not have permission to access decision history"
    )


# =========================================================
# CREATE DECISION
# =========================================================

@router.post(
    "",
    response_model=DecisionResponse,
    status_code=201
)
def create_decision(
    decision_data: DecisionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = int(current_user["sub"])

    new_decision = Decision(
        title=decision_data.title,
        problem_statement=decision_data.problem_statement,
        category=decision_data.category,
        status="Draft",
        created_by=user_id
    )

    db.add(new_decision)
    db.flush()

    create_activity_log(
        db=db,
        user_id=user_id,
        action="CREATE",
        entity_type="Decision",
        entity_id=new_decision.id,
        description=f"Created decision: {new_decision.title}"
    )

    create_audit_log(
        db=db,
        user_id=user_id,
        action="CREATE",
        entity_type="Decision",
        entity_id=new_decision.id,
        description=f"Created decision: {new_decision.title}",
        new_value={
            "title": new_decision.title,
            "problem_statement": new_decision.problem_statement,
            "category": new_decision.category,
            "status": new_decision.status,
        },
        request_method="POST",
        endpoint="/decisions",
    )

    db.commit()
    db.refresh(new_decision)

    return new_decision


# =========================================================
# GET ALL DECISIONS + FILTERING
# =========================================================

@router.get(
    "",
    response_model=List[DecisionResponse]
)
def get_decisions(
    status: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    db: Session = Depends(get_db)
):
    query = db.query(Decision)

    if status:
        query = query.filter(
            Decision.status == status
        )

    if category:
        query = query.filter(
            Decision.category == category
        )

    return query.all()


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
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    user_id = int(current_user["sub"])

    old_value = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category,
        "status": decision.status,
    }

    decision.title = decision_data.title
    decision.problem_statement = decision_data.problem_statement
    decision.category = decision_data.category

    db.flush()

    # Create sequential decision version
    create_decision_version(
        db=db,
        decision=decision,
        user_id=user_id
    )

    create_activity_log(
        db=db,
        user_id=user_id,
        action="UPDATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"Updated decision: {decision.title}"
    )

    create_audit_log(
        db=db,
        user_id=user_id,
        action="UPDATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"Updated decision: {decision.title}",
        old_value=old_value,
        new_value={
            "title": decision.title,
            "problem_statement": decision.problem_statement,
            "category": decision.category,
            "status": decision.status,
        },
        ip_address=request.client.host if request.client else None,
        request_method=request.method,
        endpoint=request.url.path,
    )

    db.commit()
    db.refresh(decision)

    return decision


# =========================================================
# UPDATE DECISION STATUS
# =========================================================

@router.patch(
    "/{decision_id}/status",
    response_model=DecisionResponse
)
def update_decision_status(
    decision_id: int,
    status_data: DecisionStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    user_id = int(current_user["sub"])

    old_status = decision.status

    decision.status = status_data.status.value

    db.flush()

    # Create sequential version for status change
    create_decision_version(
        db=db,
        decision=decision,
        user_id=user_id
    )

    create_activity_log(
        db=db,
        user_id=user_id,
        action="STATUS_CHANGE",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"Changed decision status from {old_status} to {decision.status}"
    )

    create_audit_log(
        db=db,
        user_id=user_id,
        action="UPDATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"Changed decision status from {old_status} to {decision.status}",
        old_value={
            "status": old_status
        },
        new_value={
            "status": decision.status
        },
        ip_address=request.client.host if request.client else None,
        request_method=request.method,
        endpoint=request.url.path,
    )

    db.commit()
    db.refresh(decision)

    return decision


# =========================================================
# CREATE ALTERNATIVE
# =========================================================

@router.post(
    "/{decision_id}/alternatives",
    response_model=AlternativeResponse,
    status_code=201
)
def create_alternative(
    decision_id: int,
    alternative_data: AlternativeCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    user_id = int(current_user["sub"])

    new_alternative = Alternative(
        decision_id=decision_id,
        name=alternative_data.name,
        description=alternative_data.description,
        pros=alternative_data.pros,
        cons=alternative_data.cons,
        estimated_cost=alternative_data.estimated_cost,
        feasibility_score=alternative_data.feasibility_score,
        risk_level=alternative_data.risk_level.value
    )

    db.add(new_alternative)
    db.flush()

    create_activity_log(
        db=db,
        user_id=user_id,
        action="CREATE",
        entity_type="Alternative",
        entity_id=new_alternative.id,
        description=(
            f"Created alternative for decision "
            f"{decision_id}: {new_alternative.name}"
        )
    )

    create_audit_log(
        db=db,
        user_id=user_id,
        action="CREATE",
        entity_type="Alternative",
        entity_id=new_alternative.id,
        description=(
            f"Created alternative for decision "
            f"{decision_id}: {new_alternative.name}"
        ),
        new_value={
            "decision_id": decision_id,
            "name": new_alternative.name,
            "description": new_alternative.description,
            "pros": new_alternative.pros,
            "cons": new_alternative.cons,
            "estimated_cost": new_alternative.estimated_cost,
            "feasibility_score": new_alternative.feasibility_score,
            "risk_level": new_alternative.risk_level,
        },
        ip_address=request.client.host if request.client else None,
        request_method=request.method,
        endpoint=request.url.path,
    )

    db.commit()
    db.refresh(new_alternative)

    return new_alternative


# =========================================================
# GET ALL ALTERNATIVES FOR A DECISION
# =========================================================

@router.get(
    "/{decision_id}/alternatives",
    response_model=List[AlternativeResponse]
)
def get_alternatives(
    decision_id: int,
    db: Session = Depends(get_db)
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    alternatives = (
        db.query(Alternative)
        .filter(
            Alternative.decision_id == decision_id
        )
        .all()
    )

    return alternatives


# =========================================================
# COMPARE ALTERNATIVES
# =========================================================

@router.get(
    "/{decision_id}/alternatives/compare"
)
def compare_alternatives(
    decision_id: int,
    db: Session = Depends(get_db)
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    alternatives = (
        db.query(Alternative)
        .filter(
            Alternative.decision_id == decision_id
        )
        .all()
    )

    return {
        "decision_id": decision_id,
        "alternatives": [
            {
                "name": alternative.name,
                "estimated_cost": alternative.estimated_cost,
                "feasibility_score": alternative.feasibility_score,
                "risk_level": alternative.risk_level
            }
            for alternative in alternatives
        ]
    }


# =========================================================
# ASSIGN TAGS TO DECISION
# =========================================================

@router.post(
    "/{decision_id}/tags",
    response_model=List[TagResponse]
)
def assign_tags_to_decision(
    decision_id: int,
    tag_data: DecisionTagAssign,
    db: Session = Depends(get_db)
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    tags = (
        db.query(Tag)
        .filter(Tag.id.in_(tag_data.tag_ids))
        .all()
    )

    if len(tags) != len(set(tag_data.tag_ids)):
        raise HTTPException(
            status_code=404,
            detail="One or more tags not found"
        )

    existing_tag_ids = {
        tag.id for tag in decision.tags
    }

    for tag in tags:
        if tag.id not in existing_tag_ids:
            decision.tags.append(tag)

    db.commit()
    db.refresh(decision)

    return decision.tags


# =========================================================
# GET TAGS FOR A DECISION
# =========================================================

@router.get(
    "/{decision_id}/tags",
    response_model=List[TagResponse]
)
def get_decision_tags(
    decision_id: int,
    db: Session = Depends(get_db)
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    return decision.tags


# =========================================================
# REMOVE TAG FROM DECISION
# =========================================================

@router.delete(
    "/{decision_id}/tags/{tag_id}"
)
def remove_tag_from_decision(
    decision_id: int,
    tag_id: int,
    db: Session = Depends(get_db)
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    tag = (
        db.query(Tag)
        .filter(Tag.id == tag_id)
        .first()
    )

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
        "message": "Tag removed from decision successfully"
    }


# =========================================================
# GET DECISION VERSIONS
# =========================================================

@router.get(
    "/{decision_id}/versions",
    response_model=DecisionVersionListResponse
)
def get_decision_versions(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    check_decision_history_access(
        db,
        decision,
        current_user
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

    return {
        "decision_id": decision_id,
        "versions": versions
    }


# =========================================================
# GET SPECIFIC DECISION VERSION
# =========================================================

@router.get(
    "/{decision_id}/versions/{version_number}",
    response_model=DecisionVersionResponse
)
def get_decision_version(
    decision_id: int,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    check_decision_history_access(
        db,
        decision,
        current_user
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
            status_code=404,
            detail="Decision version not found"
        )

    return version


# =========================================================
# GET DECISION HISTORY
# =========================================================

@router.get(
    "/{decision_id}/history",
    response_model=DecisionHistoryResponse
)
def get_decision_history(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    check_decision_history_access(
        db,
        decision,
        current_user
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

    return {
        "decision_id": decision_id,
        "current": decision,
        "history": versions
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
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    create_access_log(
        db=db,
        user_id=int(current_user["sub"]),
        resource_type="Decision",
        resource_id=decision.id,
        action="VIEW",
        ip_address=request.client.host if request.client else None,
    )

    db.commit()

    return decision


# =========================================================
# DELETE DECISION
# =========================================================

@router.delete(
    "/{decision_id}"
)
def delete_decision(
    decision_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail="Decision not found"
        )

    user_id = int(current_user["sub"])

    old_value = {
        "title": decision.title,
        "problem_statement": decision.problem_statement,
        "category": decision.category,
        "status": decision.status,
        "created_by": decision.created_by,
    }

    decision_title = decision.title

    db.delete(decision)
    db.flush()

    create_activity_log(
        db=db,
        user_id=user_id,
        action="DELETE",
        entity_type="Decision",
        entity_id=decision_id,
        description=f"Deleted decision: {decision_title}"
    )

    create_audit_log(
        db=db,
        user_id=user_id,
        action="DELETE",
        entity_type="Decision",
        entity_id=decision_id,
        description=f"Deleted decision: {decision_title}",
        old_value=old_value,
        request_method=request.method,
        endpoint=request.url.path,
        ip_address=request.client.host if request.client else None,
    )

    db.commit()

    return {
        "message": "Decision deleted successfully"
    }
