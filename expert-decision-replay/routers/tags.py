from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.tag import Tag
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/tags",
    tags=["Tag Management"]
)


# =========================================================
# CREATE TAG
# =========================================================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED
)
def create_tag(
    name: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Check whether tag already exists
    existing_tag = (
        db.query(Tag)
        .filter(Tag.name == name)
        .first()
    )

    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag already exists"
        )

    new_tag = Tag(
        name=name
    )

    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)

    return new_tag


# =========================================================
# GET ALL TAGS
# =========================================================

@router.get("")
def get_tags(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    tags = (
        db.query(Tag)
        .order_by(Tag.name.asc())
        .all()
    )

    return tags


# =========================================================
# GET TAG BY ID
# =========================================================

@router.get("/{tag_id}")
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


# =========================================================
# DELETE TAG
# =========================================================

@router.delete("/{tag_id}")
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