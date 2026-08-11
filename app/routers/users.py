from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
)
from app.utils.security import hash_password
from app.utils.jwt import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# ─── GET /users/me — Protected: returns the authenticated user's profile ──────
@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user"
)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the profile of the currently authenticated user.
    Requires a valid Bearer JWT. Never returns password or password_hash."""
    return current_user


# ─── POST /users — Create a new user ─────────────────────────────────────────
@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    # Check for duplicate email — 409 Conflict
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists"
        )

    # Check for duplicate employee_id — 409 Conflict
    if user.employee_id and db.query(User).filter(User.employee_id == user.employee_id).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this employee ID already exists"
        )

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password_hash=hash_password(user.password),   # hash before storing
        role=user.role,
        employee_id=user.employee_id,
        department=user.department,
        designation=user.designation,
        phone=user.phone,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ─── GET /users — List all users (authenticated) ─────────────────────────────
@router.get(
    "",
    response_model=List[UserResponse],
    summary="List all users"
)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(User).all()


# ─── GET /users/{user_id} — Get user by ID (authenticated) ───────────────────
@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID"
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


# ─── PUT /users/{user_id} — Update user (authenticated) ──────────────────────
@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user by ID"
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user_data.full_name is not None:
        user.full_name = user_data.full_name

    if user_data.email is not None:
        user.email = user_data.email

    if user_data.role is not None:
        user.role = user_data.role

    if user_data.password is not None:
        user.password_hash = hash_password(user_data.password)  # always hash

    if user_data.employee_id is not None:
        user.employee_id = user_data.employee_id

    if user_data.department is not None:
        user.department = user_data.department

    if user_data.designation is not None:
        user.designation = user_data.designation

    if user_data.phone is not None:
        user.phone = user_data.phone

    db.commit()
    db.refresh(user)

    return user


# ─── DELETE /users/{user_id} — Delete user (authenticated) ───────────────────
@router.delete(
    "/{user_id}",
    summary="Delete user by ID"
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}