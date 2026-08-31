from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.security import verify_password, create_access_token
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.audit_service import log_security

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login", response_model=TokenResponse)
def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    ip = request.client.host if request.client else None

    user = (
        db.query(User)
        .filter(User.email == login_data.email)
        .first()
    )

    if not user:
        log_security(
            db,
            event_type="LOGIN_FAILED",
            email=login_data.email,
            description=f"Failed login attempt for email: {login_data.email}",
            ip_address=ip,
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(login_data.password, user.password):
        log_security(
            db,
            event_type="LOGIN_FAILED",
            user_id=user.id,
            email=login_data.email,
            description=f"Failed login attempt for user {user.id}",
            ip_address=ip,
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(user.id)

    log_security(
        db,
        event_type="LOGIN_SUCCESS",
        user_id=user.id,
        email=login_data.email,
        description=f"User {user.id} logged in successfully",
        ip_address=ip,
    )
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }