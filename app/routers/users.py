from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse
)
from app.services.auth import get_current_user
from app.services.authorization import require_roles
from app.services.security import hash_password


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
# Manager and Administrator only
# ============================================================

@router.get(
    "",
    response_model=List[UserResponse]
)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.MANAGER,
            UserRole.ADMINISTRATOR
        )
    )
):
    return db.query(User).all()


# ============================================================
# GET USER BY ID
# Users can view themselves.
# Managers and Administrators can view anyone.
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

    # A user can view their own profile
    if current_user.id == user_id:
        return user

    # Managers and Administrators can view other users
    if current_user.role not in (
        UserRole.MANAGER,
        UserRole.ADMINISTRATOR
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this user"
        )

    return user


# ============================================================
# UPDATE USER
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

    # --------------------------------------------------------
    # Permission check
    # --------------------------------------------------------

    is_own_profile = current_user.id == user_id

    if not is_own_profile:
        if current_user.role not in (
            UserRole.MANAGER,
            UserRole.ADMINISTRATOR
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to edit this user"
            )

    # --------------------------------------------------------
    # Role change protection
    # --------------------------------------------------------

    if user_data.role is not None:

        # Users cannot change their own role
        if is_own_profile:
            if user_data.role != current_user.role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You cannot change your own role"
                )

        # Only Administrator can change another user's role
        elif current_user.role != UserRole.ADMINISTRATOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only an Administrator can change user roles"
            )

    # --------------------------------------------------------
    # Update full name
    # --------------------------------------------------------

    if user_data.full_name is not None:
        user.full_name = user_data.full_name

    # --------------------------------------------------------
    # Update email
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Update role
    # --------------------------------------------------------

    if user_data.role is not None:
        user.role = user_data.role

    # --------------------------------------------------------
    # Update employee ID
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Update department
    # --------------------------------------------------------

    if user_data.department is not None:
        user.department = user_data.department

    # --------------------------------------------------------
    # Update designation
    # --------------------------------------------------------

    if user_data.designation is not None:
        user.designation = user_data.designation

    # --------------------------------------------------------
    # Update phone number
    # --------------------------------------------------------

    if user_data.phone_number is not None:
        user.phone_number = user_data.phone_number

    # --------------------------------------------------------
    # Update password
    # --------------------------------------------------------

    if user_data.password is not None:
        user.password = hash_password(
            user_data.password
        )

    db.commit()
    db.refresh(user)

    return user


# ============================================================
# DELETE USER
# Administrator only
# ============================================================

@router.delete(
    "/{user_id}"
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMINISTRATOR
        )
    )
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

    # Prevent Administrator from accidentally deleting
    # their own account.
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }