from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.services.audit import create_security_log
from app.services.auth import get_current_user
from app.services.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    verify_password,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


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