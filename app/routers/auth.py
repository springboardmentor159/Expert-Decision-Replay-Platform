from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, Token, UserResponse
from app.services.audit_service import log_audit, log_security_event

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and return JWT token (Security & Audit Tracked)"
)
def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Authenticate user credentials and return a signed JWT access token.
    Automatically records LOGIN_SUCCESS or LOGIN_FAILED security events.
    """
    client_ip = request.client.host if request.client else None
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        # Record security log for failed login attempt (NO password stored)
        log_security_event(
            db=db,
            user_id=user.id if user else None,
            event_type="LOGIN_FAILED",
            description=f"Failed login attempt for email '{login_data.email}'",
            ip_address=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Record security log for successful login
    log_security_event(
        db=db,
        user_id=user.id,
        event_type="LOGIN_SUCCESS",
        description=f"User {user.full_name} ({user.email}) logged in successfully",
        ip_address=client_ip
    )

    # Record audit log
    log_audit(
        db=db,
        user_id=user.id,
        action="LOGIN",
        entity_type="User",
        entity_id=user.id,
        description=f"User {user.full_name} logged in successfully",
        ip_address=client_ip,
        request_method="POST",
        endpoint="/auth/login"
    )

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "user_id": user.id}
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )
