from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user

from app.models.user import User
from app.models.tag import Tag
from app.models.decision import Decision

from app.schemas.tag import (
    TagCreate,
    TagResponse,
    DecisionTagAssignment,
)


router = APIRouter(
    tags=["Tags"],
)


# =========================
# CREATE TAG
# =========================

@router.post(
    "/tags",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_tag(
    tag_data: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_tag = (
        db.query(Tag)
        .filter(Tag.name.ilike(tag_data.name))
        .first()
    )

    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tag already exists",
        )

    new_tag = Tag(
        name=tag_data.name.strip()
    )

    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)

    return new_tag


# =========================
# GET ALL TAGS
# =========================

@router.get(
    "/tags",
    response_model=List[TagResponse],
)
def get_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Tag)
        .order_by(Tag.name.asc())
        .all()
    )


# =========================
# GET TAG BY ID
# =========================

@router.get(
    "/tags/{tag_id}",
    response_model=TagResponse,
)
def get_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tag = (
        db.query(Tag)
        .filter(Tag.id == tag_id)
        .first()
    )

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    return tag


# =========================
# DELETE TAG
# =========================

@router.delete(
    "/tags/{tag_id}",
)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tag = (
        db.query(Tag)
        .filter(Tag.id == tag_id)
        .first()
    )

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    db.delete(tag)
    db.commit()

    return {
        "message": "Tag deleted successfully"
    }


# =========================
# ASSIGN TAGS TO DECISION
# =========================

@router.post(
    "/decisions/{decision_id}/tags",
    response_model=List[TagResponse],
    status_code=status.HTTP_200_OK,
)
def assign_tags_to_decision(
    decision_id: int,
    assignment: DecisionTagAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check decision exists
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    # Remove duplicate tag IDs from request
    unique_tag_ids = list(set(assignment.tag_ids))

    # Check all requested tags exist
    tags = (
        db.query(Tag)
        .filter(Tag.id.in_(unique_tag_ids))
        .all()
    )

    found_tag_ids = {tag.id for tag in tags}

    missing_tag_ids = [
        tag_id
        for tag_id in unique_tag_ids
        if tag_id not in found_tag_ids
    ]

    if missing_tag_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag(s) not found: {missing_tag_ids}",
        )

    # Existing tags already assigned to this decision
    existing_tag_ids = {
        tag.id
        for tag in decision.tags
    }

    # Add only new relationships
    for tag in tags:
        if tag.id not in existing_tag_ids:
            decision.tags.append(tag)

    db.commit()
    db.refresh(decision)

    return decision.tags


# =========================
# GET DECISION TAGS
# =========================

@router.get(
    "/decisions/{decision_id}/tags",
    response_model=List[TagResponse],
)
def get_decision_tags(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    return decision.tags


# =========================
# REMOVE TAG FROM DECISION
# =========================

@router.delete(
    "/decisions/{decision_id}/tags/{tag_id}",
)
def remove_tag_from_decision(
    decision_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = (
        db.query(Decision)
        .filter(Decision.id == decision_id)
        .first()
    )

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    tag = (
        db.query(Tag)
        .filter(Tag.id == tag_id)
        .first()
    )

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    if tag not in decision.tags:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag is not assigned to this decision",
        )

    decision.tags.remove(tag)

    db.commit()

    return {
        "message": "Tag removed from decision successfully"
    }