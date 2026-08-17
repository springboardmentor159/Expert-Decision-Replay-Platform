from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import hash_password
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# CREATE USER (Public Registration)
@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    # Check if email is already registered
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if employee_id is already registered
    existing_employee = db.query(User).filter(User.employee_id == user.employee_id).first()
    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee ID already registered"
        )

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        role=user.role,
        password=hash_password(user.password),
        employee_id=user.employee_id,
        department=user.department,
        designation=user.designation,
        phone_number=user.phone_number
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# GET ALL USERS (Protected)
@router.get(
    "",
    response_model=List[UserResponse]
)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(User).all()


# GET USER BY ID (Protected)
@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# UPDATE USER (Protected)
@router.put(
    "/{user_id}",
    response_model=UserResponse
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user_data.full_name is not None:
        user.full_name = user_data.full_name

    if user_data.email is not None:
        existing = db.query(User).filter(User.email == user_data.email, User.id != user_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        user.email = user_data.email

    if user_data.role is not None:
        user.role = user_data.role

    if user_data.password is not None:
        user.password = hash_password(user_data.password)

    if user_data.employee_id is not None:
        existing = db.query(User).filter(User.employee_id == user_data.employee_id, User.id != user_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID already registered"
            )
        user.employee_id = user_data.employee_id

    if user_data.department is not None:
        user.department = user_data.department

    if user_data.designation is not None:
        user.designation = user_data.designation

    if user_data.phone_number is not None:
        user.phone_number = user_data.phone_number

    db.commit()
    db.refresh(user)

    return user


# DELETE USER (Protected)
@router.delete(
    "/{user_id}"
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }