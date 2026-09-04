
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.models.decision import Decision
from app.models.alternative import Alternative
from app.models.tag import Tag

from app.schemas import decision
from app.schemas.decision import (
    DecisionCreate,
    DecisionResponse,
    DecisionUpdate,
    DecisionStatusUpdate,
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


router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"],
    dependencies=[Depends(get_current_user)]
)


# =========================================================
# CREATE DECISION
# =========================================================


@router.post("", response_model=DecisionResponse, status_code=201)
def create_decision(
    decision_data: DecisionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    new_decision = Decision(
        title=decision_data.title,
        problem_statement=decision_data.problem_statement,
        category=decision_data.category,
        status="Draft",
        created_by=int(current_user["sub"])
    )

    db.add(new_decision)
    db.flush()

    create_activity_log(
        db=db,
        user_id=int(current_user["sub"]),
        action="CREATE",
        entity_type="Decision",
        entity_id=new_decision.id,
        description=f"Created decision: {new_decision.title}"
    )

    create_audit_log(
        db=db,
        user_id=int(current_user["sub"]),
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

    decision.title = decision_data.title
    decision.problem_statement = decision_data.problem_statement
    decision.category = decision_data.category

    db.commit()
    db.refresh(decision)

    create_activity_log(
        db=db,
        user_id=int(current_user["sub"]),
        action="UPDATE",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"Updated decision: {decision.title}"
    )

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

    old_status = decision.status

    decision.status = status_data.status.value

    db.commit()
    db.refresh(decision)

    create_activity_log(
        db=db,
        user_id=int(current_user["sub"]),
        action="STATUS_CHANGE",
        entity_type="Decision",
        entity_id=decision.id,
        description=f"Changed decision status from {old_status} to {decision.status}"
    )

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
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Check whether Decision exists
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

    # Create Alternative
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
    db.commit()
    db.refresh(new_alternative)

    create_activity_log(
        db=db,
        user_id=int(current_user["sub"]),
        action="CREATE",
        entity_type="Alternative",
        entity_id=new_alternative.id,
        description=f"Created alternative for decision {decision_id}: {new_alternative.name}"
    )

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
    # Check whether Decision exists
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
    # Check whether Decision exists
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
    # Check whether Decision exists
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

    # Check whether all tags exist
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

    # Prevent duplicate relationships
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
    # Check whether Decision exists
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
    # Check whether Decision exists
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

    # Check whether Tag exists
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

    # Check whether tag is assigned to this decision
    if tag not in decision.tags:
        raise HTTPException(
            status_code=404,
            detail="Tag is not assigned to this decision"
        )

    # Remove only the relationship
    decision.tags.remove(tag)

    db.commit()

    return {
        "message": "Tag removed from decision successfully"
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

    return decision


# =========================================================
# DELETE DECISION
# =========================================================

@router.delete(
    "/{decision_id}"
)
def delete_decision(
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

    decision_title = decision.title

    db.delete(decision)
    db.commit()

    create_activity_log(
        db=db,
        user_id=int(current_user["sub"]),
        action="DELETE",
        entity_type="Decision",
        entity_id=decision_id,
        description=f"Deleted decision: {decision_title}"
    )

    return {
        "message": "Decision deleted successfully"
    }