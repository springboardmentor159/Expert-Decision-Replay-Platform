from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagResponse
from app.routers.auth import get_current_user


router = APIRouter(
    prefix="/tags",
    tags=["Tags"]
)


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
    tag_name = tag_data.name.strip()

    if not tag_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Tag name cannot be empty"
        )

    existing_tag = (
        db.query(Tag)
        .filter(Tag.name == tag_name)
        .first()
    )

    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag already exists"
        )

    tag = Tag(name=tag_name)

    db.add(tag)
    db.commit()
    db.refresh(tag)

    return tag


@router.get(
    "",
    response_model=list[TagResponse],
    status_code=status.HTTP_200_OK
)
def get_tags(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return (
        db.query(Tag)
        .order_by(Tag.name.asc())
        .all()
    )


@router.get(
    "/{tag_id}",
    response_model=TagResponse,
    status_code=status.HTTP_200_OK
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


@router.delete(
    "/{tag_id}",
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

    if tag.decisions:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tag is assigned to one or more decisions"
        )

    db.delete(tag)
    db.commit()

    return None