from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagResponse
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/tags",
    tags=["Tags"],
    dependencies=[Depends(get_current_user)]
)


# =========================================================
# CREATE TAG
# =========================================================

@router.post(
    "",
    response_model=TagResponse,
    status_code=201
)
def create_tag(
    tag_data: TagCreate,
    db: Session = Depends(get_db)
):
    # Check whether tag already exists
    existing_tag = (
        db.query(Tag)
        .filter(Tag.name == tag_data.name)
        .first()
    )

    if existing_tag:
        raise HTTPException(
            status_code=400,
            detail="Tag already exists"
        )

    new_tag = Tag(
        name=tag_data.name
    )

    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)

    return new_tag


# =========================================================
# GET ALL TAGS
# =========================================================

@router.get(
    "",
    response_model=List[TagResponse]
)
def get_tags(
    db: Session = Depends(get_db)
):
    return (
        db.query(Tag)
        .order_by(Tag.name.asc())
        .all()
    )


# =========================================================
# GET TAG BY ID
# =========================================================

@router.get(
    "/{tag_id}",
    response_model=TagResponse
)
def get_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
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

    return tag


# =========================================================
# DELETE TAG
# =========================================================

@router.delete(
    "/{tag_id}"
)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
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

    db.delete(tag)
    db.commit()

    return {
        "message": "Tag deleted successfully"
    }