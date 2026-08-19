from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import (
    LoginRequest,
    Token,
    UserCreate,
    UserResponse,
    UserUpdate,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# REGISTER / CREATE USER (Public)
@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    if user.employee_id:
        existing_emp = db.query(User).filter(User.employee_id == user.employee_id).first()
        if existing_emp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID already registered"
            )

    hashed_pwd = hash_password(user.password)

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        role=user.role.value if hasattr(user.role, "value") else str(user.role),
        hashed_password=hashed_pwd,
        employee_id=user.employee_id,
        department=user.department,
        designation=user.designation,
        phone_number=user.phone_number,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# USER LOGIN ALIAS (Public)
@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK
)
def login_user(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "user_id": user.id}
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


# GET CURRENT LOGGED-IN USER PROFILE (Protected)
@router.get(
    "/me",
    response_model=UserResponse
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user


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
            status_code=status.HTTP_404_NOT_FOUND,
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user_data.full_name is not None:
        user.full_name = user_data.full_name

    if user_data.email is not None and user_data.email != user.email:
        existing_user = db.query(User).filter(User.email == user_data.email, User.id != user_id).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        user.email = user_data.email

    if user_data.employee_id is not None and user_data.employee_id != user.employee_id:
        existing_emp = db.query(User).filter(User.employee_id == user_data.employee_id, User.id != user_id).first()
        if existing_emp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID already registered"
            )
        user.employee_id = user_data.employee_id

    if user_data.role is not None:
        user.role = user_data.role.value if hasattr(user_data.role, "value") else str(user_data.role)

    if user_data.password is not None:
        user.hashed_password = hash_password(user_data.password)


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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }