from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.models.tag import Tag
from app.models.user import User
from app.schemas.tag import TagCreate, TagResponse

router = APIRouter(prefix="/tags", tags=["Tags"])


def _require_manager(current_user: User) -> None:
    if current_user.role not in {"admin", "manager", "Administrator", "Manager"}:
        raise HTTPException(status_code=403, detail="Insufficient permission")


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(payload: TagCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_manager(current_user)
    tag = Tag(name=payload.name.strip())
    if db.query(Tag).filter(Tag.name.ilike(tag.name)).first():
        raise HTTPException(status_code=409, detail="Tag already exists")
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.get("", response_model=list[TagResponse])
def list_tags(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Tag).order_by(Tag.name.asc()).all()


@router.get("/{tag_id}", response_model=TagResponse)
def get_tag(tag_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_manager(current_user)
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
    db.commit()