from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagResponse
from app.routers.users import get_current_user

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(tag_data: TagCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    tag = Tag(name=tag_data.name.strip())
    if not tag.name:
        raise HTTPException(status_code=422, detail="Tag name cannot be empty")
    db.add(tag)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Tag already exists")
    db.refresh(tag)
    return tag


@router.get("", response_model=list[TagResponse])
def get_tags(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Tag).order_by(Tag.name.asc()).all()


@router.get("/{tag_id}", response_model=TagResponse)
def get_tag(tag_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
    db.commit()