from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import get_current_user, hash_password


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ---------------------------------------------------------
# GET ALL USERS
# ---------------------------------------------------------
@router.get(
    "",
    response_model=List[UserResponse],
)
def get_users(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    users = db.query(User).all()
    return users


# ---------------------------------------------------------
# CREATE USER
# ---------------------------------------------------------
@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    # Check duplicate email
    existing_email = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )

    # Check duplicate employee ID
    existing_employee = (
        db.query(User)
        .filter(User.employee_id == user.employee_id)
        .first()
    )

    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee ID already exists",
        )

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        role=user.role.value,
        password=hash_password(user.password),
        employee_id=user.employee_id,
        department=user.department,
        designation=user.designation,
        phone_number=user.phone_number,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ---------------------------------------------------------
# GET USER BY ID
# ---------------------------------------------------------
@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


# ---------------------------------------------------------
# UPDATE USER
# ---------------------------------------------------------
@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: int,
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check duplicate email
    existing_email = (
        db.query(User)
        .filter(
            User.email == user_data.email,
            User.id != user_id,
        )
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )

    # Check duplicate employee ID
    existing_employee = (
        db.query(User)
        .filter(
            User.employee_id == user_data.employee_id,
            User.id != user_id,
        )
        .first()
    )

    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee ID already exists",
        )

    user.full_name = user_data.full_name
    user.email = user_data.email
    user.role = user_data.role.value
    user.password = hash_password(user_data.password)
    user.employee_id = user_data.employee_id
    user.department = user_data.department
    user.designation = user_data.designation
    user.phone_number = user_data.phone_number

    db.commit()
    db.refresh(user)

    return user


# ---------------------------------------------------------
# DELETE USER
# ---------------------------------------------------------
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully",
        "user_id": user_id,
    }