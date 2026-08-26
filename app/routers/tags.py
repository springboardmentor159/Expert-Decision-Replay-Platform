from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.tag import Tag
from app.models.user import User
from app.schemas.tag import TagCreate, TagResponse
from app.services.activity_logger import log_activity

router = APIRouter(
    prefix="/tags",
    tags=["Tags"]
)


@router.post(
    "",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tag"
)
def create_tag(
    tag_data: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    name_clean = tag_data.name.strip()
    if not name_clean:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Tag name cannot be empty"
        )

    existing_tag = db.query(Tag).filter(Tag.name.ilike(name_clean)).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag '{name_clean}' already exists"
        )

    new_tag = Tag(name=name_clean)
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="create",
        entity_type="Tag",
        entity_id=new_tag.id,
        description=f"User {current_user.full_name} created tag '{new_tag.name}'"
    )

    return new_tag


@router.get(
    "",
    response_model=List[TagResponse],
    summary="Get all tags"
)
def get_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Tag).order_by(Tag.name.asc()).all()


@router.get(
    "/{tag_id}",
    response_model=TagResponse,
    summary="Get tag by ID"
)
def get_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    return tag


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a tag"
)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    tag_name = tag.name
    db.delete(tag)
    db.commit()

    log_activity(
        db=db,
        user_id=current_user.id,
        action="delete",
        entity_type="Tag",
        entity_id=tag_id,
        description=f"User {current_user.full_name} deleted tag '{tag_name}'"
    )

    return {"message": "Tag deleted successfully"}
