from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        role=user.role,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get(
    "",
    response_model=List[UserResponse]
)
def get_users(
    db: Session = Depends(get_db)
):
    users = db.query(User).all()
    return users
