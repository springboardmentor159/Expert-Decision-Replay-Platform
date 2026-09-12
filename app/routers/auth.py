from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import (
    verify_password,
    create_access_token,
    get_password_hash,
)

from app.db.database import get_db
from app.models.user import User
from app.models.security_log import SecurityLog
from app.schemas.user import UserRegister


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ============================================================
# REGISTER
# POST /auth/register
# ============================================================

@router.post("/register")
def register(
    user_data: UserRegister,
    request: Request,
    db: Session = Depends(get_db)
):
    # --------------------------------------------------------
    # CHECK WHETHER EMAIL ALREADY EXISTS
    # --------------------------------------------------------

    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # --------------------------------------------------------
    # CHECK WHETHER EMPLOYEE ID ALREADY EXISTS
    # --------------------------------------------------------

    existing_employee = (
        db.query(User)
        .filter(User.employee_id == user_data.employee_id)
        .first()
    )

    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee ID already registered"
        )

    # --------------------------------------------------------
    # CREATE USER
    # --------------------------------------------------------

    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        role="Employee",
        hashed_password=get_password_hash(user_data.password),
        employee_id=user_data.employee_id,
        department=user_data.department,
        designation=user_data.designation,
        phone_number=user_data.phone_number
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # --------------------------------------------------------
    # SECURITY LOG
    # --------------------------------------------------------

    security_log = SecurityLog(
        user_id=new_user.id,
        event_type="REGISTRATION_SUCCESS",
        description=(
            f"User {new_user.id} registered successfully"
        ),
        ip_address=(
            request.client.host
            if request.client
            else None
        )
    )

    db.add(security_log)
    db.commit()

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "message": "Registration successful",
        "user": {
            "id": new_user.id,
            "full_name": new_user.full_name,
            "email": new_user.email,
            "role": new_user.role,
            "employee_id": new_user.employee_id,
            "department": new_user.department,
            "designation": new_user.designation,
            "phone_number": new_user.phone_number
        }
    }


# ============================================================
# LOGIN
# POST /auth/login
# ============================================================

@router.post("/login")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # GET USER
    # --------------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.email == form_data.username
        )
        .first()
    )

    # --------------------------------------------------------
    # FAILED LOGIN - USER NOT FOUND
    # --------------------------------------------------------

    if not user:

        security_log = SecurityLog(
            user_id=None,
            event_type="LOGIN_FAILED",
            description=(
                f"Failed login attempt for "
                f"email {form_data.username}"
            ),
            ip_address=(
                request.client.host
                if request.client
                else None
            )
        )

        db.add(security_log)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # --------------------------------------------------------
    # FAILED LOGIN - WRONG PASSWORD
    # --------------------------------------------------------

    if not verify_password(
        form_data.password,
        user.hashed_password
    ):

        security_log = SecurityLog(
            user_id=user.id,
            event_type="LOGIN_FAILED",
            description=(
                f"Failed login attempt for "
                f"User {user.id}"
            ),
            ip_address=(
                request.client.host
                if request.client
                else None
            )
        )

        db.add(security_log)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # --------------------------------------------------------
    # CREATE JWT TOKEN
    # --------------------------------------------------------

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role
        }
    )

    # --------------------------------------------------------
    # SUCCESSFUL LOGIN SECURITY LOG
    # --------------------------------------------------------

    security_log = SecurityLog(
        user_id=user.id,
        event_type="LOGIN_SUCCESS",
        description=(
            f"User {user.id} logged in successfully"
        ),
        ip_address=(
            request.client.host
            if request.client
            else None
        )
    )

    db.add(security_log)
    db.commit()

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }