from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse
)
from app.services.security import hash_password
from app.services.auth import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# ============================================================
# CREATE USER
# ============================================================

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    # Check whether email already exists
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check whether employee ID already exists
    if user.employee_id:
        existing_employee = (
            db.query(User)
            .filter(User.employee_id == user.employee_id)
            .first()
        )

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


# ============================================================
# GET ALL USERS
# Protected endpoint
# ============================================================

@router.get(
    "",
    response_model=List[UserResponse]
)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(User).all()


# ============================================================
# GET USER BY ID
# Protected endpoint
# ============================================================

@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


# ============================================================
# UPDATE USER
# Protected endpoint
# ============================================================

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
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update full name
    if user_data.full_name is not None:
        user.full_name = user_data.full_name

    # Update email
    if user_data.email is not None:

        existing_user = (
            db.query(User)
            .filter(
                User.email == user_data.email,
                User.id != user_id
            )
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        user.email = user_data.email

    # Update role
    if user_data.role is not None:
        user.role = user_data.role

    # Update employee ID
    if user_data.employee_id is not None:

        existing_employee = (
            db.query(User)
            .filter(
                User.employee_id == user_data.employee_id,
                User.id != user_id
            )
            .first()
        )

        if existing_employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID already registered"
            )

        user.employee_id = user_data.employee_id

    # Update department
    if user_data.department is not None:
        user.department = user_data.department

    # Update designation
    if user_data.designation is not None:
        user.designation = user_data.designation

    # Update phone number
    if user_data.phone_number is not None:
        user.phone_number = user_data.phone_number

    # Update password
    if user_data.password is not None:
        user.password = hash_password(
            user_data.password
        )

    db.commit()
    db.refresh(user)

    return user


# ============================================================
# DELETE USER
# Protected endpoint
# ============================================================

@router.delete(
    "/{user_id}"
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }