from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.security_log import SecurityLog
from app.models.role import UserRole
from app.schemas.user import UserLogin, UserRegister
from app.schemas.token import Token
from app.core.security import (
    verify_password,
    hash_password,
    create_access_token,
    get_current_user,
)

router = APIRouter(tags=["Auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserRegister,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Public registration endpoint.

    All publicly registered users are created as Employees.
    Privileged roles must be assigned by an Administrator.
    """

    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        role=UserRole.EMPLOYEE,
        hashed_password=hash_password(user_data.password),
        employee_id=user_data.employee_id,
        department=user_data.department,
        designation=user_data.designation,
        phone_number=user_data.phone_number,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    ip_address = request.client.host if request.client else None

    security_log = SecurityLog(
        user_id=new_user.id,
        event_type="REGISTER_SUCCESS",
        description="Public user registration successful",
        ip_address=ip_address,
    )

    db.add(security_log)
    db.commit()

    return {
        "message": "Registration successful",
        "user": {
            "id": new_user.id,
            "full_name": new_user.full_name,
            "email": new_user.email,
            "role": new_user.role,
        },
    }


@router.post("/login")
def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == credentials.email)
        .first()
    )

    ip_address = request.client.host if request.client else None

    # Invalid login
    if not user or not verify_password(
        credentials.password,
        user.hashed_password,
    ):
        security_log = SecurityLog(
            user_id=user.id if user else None,
            event_type="LOGIN_FAILURE",
            description="Failed login attempt",
            ip_address=ip_address,
        )

        db.add(security_log)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Successful login
    security_log = SecurityLog(
        user_id=user.id,
        event_type="LOGIN_SUCCESS",
        description="User logged in successfully",
        ip_address=ip_address,
    )

    db.add(security_log)
    db.commit()

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "employee_id": user.employee_id,
            "department": user.department,
            "designation": user.designation,
            "phone_number": user.phone_number,
        },
    }


@router.post("/logout")
def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ip_address = request.client.host if request.client else None

    security_log = SecurityLog(
        user_id=current_user.id,
        event_type="LOGOUT",
        description="User logged out",
        ip_address=ip_address,
    )

    db.add(security_log)
    db.commit()

    return {
        "message": "Logout successful"
    }