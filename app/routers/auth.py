from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User

from app.core.security import (
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

from app.services.security import log_security_event


router = APIRouter(
    tags=["Authentication"]
)


@router.post("/login")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # username field contains the user's email

    user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    # -----------------------------------------------------
    # LOGIN FAILED - USER NOT FOUND
    # -----------------------------------------------------

    if not user:

        log_security_event(
            db=db,
            event_type="LOGIN_FAILED",
            user_id=None,
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

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # -----------------------------------------------------
    # LOGIN FAILED - INVALID PASSWORD
    # -----------------------------------------------------

    if not verify_password(
        form_data.password,
        user.password
    ):

        log_security_event(
            db=db,
            event_type="LOGIN_FAILED",
            user_id=user.id,
            description=(
                f"Failed login attempt for "
                f"user {user.id}"
            ),
            ip_address=(
                request.client.host
                if request.client
                else None
            )
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # -----------------------------------------------------
    # CREATE JWT
    # -----------------------------------------------------

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value
        },
        expires_delta=timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    # -----------------------------------------------------
    # LOGIN SUCCESS
    # -----------------------------------------------------

    log_security_event(
        db=db,
        event_type="LOGIN_SUCCESS",
        user_id=user.id,
        description=(
            f"User {user.id} logged in successfully"
        ),
        ip_address=(
            request.client.host
            if request.client
            else None
        )
    )

    db.commit()

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
