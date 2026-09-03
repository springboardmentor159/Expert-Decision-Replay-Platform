from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.models.user import User
from app.models.tag import Tag
from app.routers.auth import get_current_user

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

    return new_decision


# ============================================================
# GET ALL DECISIONS
# GET /decisions/
# ============================================================

@router.get("/", response_model=list[DecisionResponse])
def get_all_decisions(
    status: DecisionStatus | None = Query(default=None),
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Decision)

    if status is not None:
        query = query.filter(Decision.status == status.value)

    if category is not None:
        query = query.filter(Decision.category == category)

    return query.all()


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

    if decision_data.title is not None:
        decision.title = decision_data.title

    if decision_data.problem_statement is not None:
        decision.problem_statement = decision_data.problem_statement

    if decision_data.category is not None:
        decision.category = decision_data.category

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