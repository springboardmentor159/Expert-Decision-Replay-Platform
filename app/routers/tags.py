from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagResponse
from app.core.security import get_current_user


router = APIRouter(
    tags=["Tags"]
)


# CREATE TAG
@router.post(
    "/tags",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED
)
def create_tag(
    tag_data: TagCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    existing_tag = (
        db.query(Tag)
        .filter(Tag.name == tag_data.name)
        .first()
    )

    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag already exists"
        )

    new_tag = Tag(
        name=tag_data.name
    )

    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)

    return new_tag


# GET ALL TAGS
@router.get(
    "/tags",
    response_model=List[TagResponse]
)
def get_tags(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(Tag).all()


# GET TAG BY ID
@router.get(
    "/tags/{tag_id}",
    response_model=TagResponse
)
def get_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    tag = (
        db.query(Tag)
        .filter(Tag.id == tag_id)
        .first()
    )

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    return tag


# DELETE TAG
@router.delete(
    "/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    tag = (
        db.query(Tag)
        .filter(Tag.id == tag_id)
        .first()
    )

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    db.delete(tag)
    db.commit()

    return None