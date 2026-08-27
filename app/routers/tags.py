from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagResponse

from app.routers.auth import get_current_user


router = APIRouter(
    prefix="/tags",
    tags=["Tags"]
)


# ----------------------------------------
# Create Tag
# ----------------------------------------

@router.post(
    "",
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


# ----------------------------------------
# Get All Tags
# ----------------------------------------

@router.get(
    "",
    response_model=List[TagResponse]
)
def get_all_tags(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return db.query(Tag).all()


# ----------------------------------------
# Get Tag By ID
# ----------------------------------------

@router.get(
    "/{tag_id}",
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

    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    return tag


# ----------------------------------------
# Update Tag
# ----------------------------------------

@router.put(
    "/{tag_id}",
    response_model=TagResponse
)
def update_tag(
    tag_id: int,
    tag_data: TagCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    tag = (
        db.query(Tag)
        .filter(Tag.id == tag_id)
        .first()
    )

    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    tag.name = tag_data.name

    db.commit()
    db.refresh(tag)

    return tag


# ----------------------------------------
# Delete Tag
# ----------------------------------------

@router.delete(
    "/{tag_id}"
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

    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    db.delete(tag)
    db.commit()

    return {
        "message": "Tag deleted successfully"
    }