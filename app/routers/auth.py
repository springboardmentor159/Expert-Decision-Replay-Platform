from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.core.security import (
    verify_password,
    create_access_token,
    get_current_user,
)
from app.services.security import create_security_log


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------
@router.post("/login")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else None

    user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    # -----------------------------------------------------
    # LOGIN FAILURE - USER NOT FOUND
    # -----------------------------------------------------
    if not user:
        create_security_log(
            db=db,
            user_id=None,
            event_type="LOGIN_FAILURE",
            description="Login failed: invalid email or password",
            ip_address=client_ip,
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # -----------------------------------------------------
    # LOGIN FAILURE - WRONG PASSWORD
    # -----------------------------------------------------
    if not verify_password(
        form_data.password,
        user.password
    ):
        create_security_log(
            db=db,
            user_id=user.id,
            event_type="LOGIN_FAILURE",
            description="Login failed: invalid email or password",
            ip_address=client_ip,
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # -----------------------------------------------------
    # CREATE JWT
    # -----------------------------------------------------
    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    # -----------------------------------------------------
    # LOGIN SUCCESS SECURITY LOG
    # -----------------------------------------------------
    create_security_log(
        db=db,
        user_id=user.id,
        event_type="LOGIN_SUCCESS",
        description="User login successful",
        ip_address=client_ip,
    )

    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------
@router.post("/logout")
def logout(
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    client_ip = request.client.host if request.client else None

    create_security_log(
        db=db,
        user_id=current_user.id,
        event_type="LOGOUT",
        description="User logout recorded",
        ip_address=client_ip,
    )

    db.commit()

    return {
        "message": "Logout recorded successfully"
    }