from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import Decision
from app.models.tag import Tag
from app.models.user import User
from app.schemas.tag import TagCreate, TagResponse
from app.core.security import get_current_user


router = APIRouter(
    tags=["Tags"]
)


# ==========================================
# CREATE TAG
# ==========================================
@router.post(
    "/tags",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_tag = db.query(Tag).filter(
        Tag.name == tag.name
    ).first()

    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag already exists",
        )

    new_tag = Tag(
        name=tag.name
    )

    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)

    return new_tag


# ==========================================
# GET ALL TAGS
# ==========================================
@router.get(
    "/tags",
    response_model=List[TagResponse],
)
def get_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Tag).all()


# ==========================================
# GET TAG BY ID
# ==========================================
@router.get(
    "/tags/{tag_id}",
    response_model=TagResponse,
)
def get_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tag = db.query(Tag).filter(
        Tag.id == tag_id
    ).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    return tag


# ==========================================
# GET ALL TAGS FOR A DECISION
# ==========================================
@router.get(
    "/decisions/{decision_id}/tags",
    response_model=List[TagResponse],
)
def get_decision_tags(
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    return decision.tags


# ==========================================
# DELETE TAG
# ==========================================
@router.delete(
    "/tags/{tag_id}",
    status_code=status.HTTP_200_OK,
)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tag = db.query(Tag).filter(
        Tag.id == tag_id
    ).first()

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


# ==========================================
# ASSIGN TAG TO DECISION
# ==========================================
@router.post(
    "/decisions/{decision_id}/tags/{tag_id}",
    response_model=TagResponse,
)
def assign_tag_to_decision(
    decision_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    tag = db.query(Tag).filter(
        Tag.id == tag_id
    ).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    if tag in decision.tags:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag is already assigned to this decision",
        )

    decision.tags.append(tag)

    db.commit()
    db.refresh(tag)

    return tag


# ==========================================
# REMOVE TAG FROM DECISION
# ==========================================
@router.delete(
    "/decisions/{decision_id}/tags/{tag_id}",
    status_code=status.HTTP_200_OK,
)
def remove_tag_from_decision(
    decision_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found",
        )

    tag = db.query(Tag).filter(
        Tag.id == tag_id
    ).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    if tag not in decision.tags:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag is not assigned to this decision",
        )

    decision.tags.remove(tag)

    db.commit()

    return {
        "message": "Tag removed from decision successfully"
    }