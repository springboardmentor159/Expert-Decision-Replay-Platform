from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.security_log import SecurityLog

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin
)


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


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

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        role=user.role.value,
        hashed_password=hash_password(user.password),

        employee_id=user.employee_id,
        department=user.department,
        designation=user.designation,
        phone_number=user.phone_number
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# =========================================================
# GET ALL USERS
# =========================================================

@router.get(
    "",
    response_model=List[UserResponse]
)
def get_users(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return db.query(User).order_by(User.id).all()


# =========================================================
# LOGIN USER
# =========================================================

@router.post("/login")
def login_user(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    # -----------------------------------------------------
    # Failed login - user does not exist
    # -----------------------------------------------------

    if not user:

        # No user_id because the user does not exist
        security_log = SecurityLog(
            user_id=None,
            event_type="LOGIN_FAILED",
            description="Login failed: user not found",
            ip_address=None
        )

        db.add(security_log)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # -----------------------------------------------------
    # Failed login - wrong password
    # -----------------------------------------------------

    if not verify_password(
        user_data.password,
        user.hashed_password
    ):

        security_log = SecurityLog(
            user_id=user.id,
            event_type="LOGIN_FAILED",
            description="Login failed: invalid password",
            ip_address=None
        )

        db.add(security_log)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # -----------------------------------------------------
    # Successful login
    # -----------------------------------------------------

    security_log = SecurityLog(
        user_id=user.id,
        event_type="LOGIN_SUCCESS",
        description=f"User {user.id} logged in successfully",
        ip_address=None
    )

    db.add(security_log)
    db.commit()

    # -----------------------------------------------------
    # Create JWT
    # -----------------------------------------------------

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# =========================================================
# GET USER BY ID
# =========================================================

@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# =========================================================
# UPDATE USER
# =========================================================

@router.put(
    "/{user_id}",
    response_model=UserResponse
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user_data.full_name is not None:
        user.full_name = user_data.full_name

    if user_data.email is not None:
        user.email = user_data.email

    if user_data.role is not None:
        user.role = user_data.role.value

    if user_data.employee_id is not None:
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


# =========================================================
# DELETE USER
# =========================================================

@router.delete(
    "/{user_id}"
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    user = db.query(User).filter(
        User.id == user_id
    ).first()

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