from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import hash_password


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# =========================================================
# GET ALL USERS
# =========================================================

@router.get(
    "",
    response_model=List[UserResponse]
)
def get_users(
    db: Session = Depends(get_db)
):
    users = db.query(User).all()
    return users


# =========================================================
# CREATE USER
# =========================================================

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # CHECK DUPLICATE EMAIL
    # -----------------------------------------------------

    existing_user = (
        db.query(User)
        .filter(User.email == str(user.email))
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # -----------------------------------------------------
    # CHECK DUPLICATE EMPLOYEE ID
    # -----------------------------------------------------

    existing_employee = (
        db.query(User)
        .filter(User.employee_id == user.employee_id)
        .first()
    )

    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee ID already registered"
        )

    # -----------------------------------------------------
    # CREATE USER
    # -----------------------------------------------------

    new_user = User(
        full_name=user.full_name,
        employee_id=user.employee_id,
        email=str(user.email),
        department=user.department,
        designation=user.designation,
        phone_number=user.phone_number,
        role=(
            user.role.value
            if hasattr(user.role, "value")
            else user.role
        ),
        password=hash_password(user.password)
    )

    db.add(new_user)

    # -----------------------------------------------------
    # DATABASE CONFLICT HANDLING
    # -----------------------------------------------------

    try:
        db.commit()
        db.refresh(new_user)

    except IntegrityError as e:
        db.rollback()

        error_message = str(e.orig).lower()

        if "employee_id" in error_message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee ID already registered"
            )

        if "email" in error_message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )

    return new_user