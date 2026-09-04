from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services.audit import create_security_log
from app.services.auth import get_current_user
from app.services.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    hash_password,
    verify_password,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    ip_address = request.client.host if request.client else None

    # Verify organization exists
    organization = (
        db.query(Organization)
        .filter(Organization.id == user_data.organization_id)
        .first()
    )
    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Check duplicate email
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check duplicate employee ID
    if user_data.employee_id:
        existing_employee = (
            db.query(User)
            .filter(User.employee_id == user_data.employee_id)
            .first()
        )
        if existing_employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID already registered",
            )

    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        role=user_data.role,
        password=hash_password(user_data.password),
        employee_id=user_data.employee_id,
        department=user_data.department,
        designation=user_data.designation,
        phone_number=user_data.phone_number,
        organization_id=user_data.organization_id,
    )

    db.add(new_user)
    db.flush()

    create_security_log(
        db=db,
        event_type="USER_REGISTERED",
        description=f"User '{new_user.email}' registered with role '{new_user.role.value}'",
        user_id=new_user.id,
        email=new_user.email,
        ip_address=ip_address,
    )
    db.commit()
    db.refresh(new_user)

    return new_user



@router.post("/login")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    ip_address = request.client.host if request.client else None

    # Swagger/OAuth2 calls the login field "username".
    # We use the user's email as the username.
    user = (
        db.query(User)
        .filter(User.email == form_data.username)
        .first()
    )

    if user is None:
        create_security_log(
            db=db,
            event_type="LOGIN_FAILED",
            description=f"Failed login attempt for non-existent email '{form_data.username}'",
            email=form_data.username,
            ip_address=ip_address,
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    if not verify_password(
        form_data.password,
        user.password
    ):
        create_security_log(
            db=db,
            event_type="LOGIN_FAILED",
            description=f"Failed login attempt (wrong password) for user '{user.email}'",
            user_id=user.id,
            email=user.email,
            ip_address=ip_address,
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    create_security_log(
        db=db,
        event_type="LOGIN_SUCCESS",
        description=f"User '{user.email}' logged in successfully",
        user_id=user.id,
        email=user.email,
        ip_address=ip_address,
    )
    db.commit()

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }



@router.get("/me")
def get_logged_in_user(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role.value,
        "employee_id": current_user.employee_id,
        "department": current_user.department,
        "designation": current_user.designation,
        "phone_number": current_user.phone_number
    }
