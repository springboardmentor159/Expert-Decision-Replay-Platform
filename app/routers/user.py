from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")

    if db.query(User).filter(User.employee_id == user.employee_id).first():
        raise HTTPException(status_code=409, detail="Employee ID already registered")

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        role=user.role.value,
        employee_id=user.employee_id,
        department=user.department,
        designation=user.designation,
        phone_number=user.phone_number,
        password=hash_password(user.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()

    if user is None or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }


@router.get("", response_model=List[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(User).all()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_data.email is not None and user_data.email != user.email:
        if db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(status_code=409, detail="Email already registered")
        user.email = user_data.email

    if user_data.employee_id is not None and user_data.employee_id != user.employee_id:
        if db.query(User).filter(User.employee_id == user_data.employee_id).first():
            raise HTTPException(status_code=409, detail="Employee ID already registered")
        user.employee_id = user_data.employee_id

    if user_data.full_name is not None:
        user.full_name = user_data.full_name

    if user_data.role is not None:
        user.role = user_data.role.value

    if user_data.department is not None:
        user.department = user_data.department

    if user_data.designation is not None:
        user.designation = user_data.designation

    if user_data.phone_number is not None:
        user.phone_number = user_data.phone_number

    if user_data.password is not None:
        user.password = hash_password(user_data.password)

    db.commit()
    db.refresh(user)

    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}