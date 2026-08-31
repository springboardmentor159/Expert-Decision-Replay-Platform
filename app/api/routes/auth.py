from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, verify_password
from app.db.database import get_db
from app.models.user import User
from app.services.audit import log_audit, log_security

router = APIRouter(
    prefix="/login",
    tags=["Auth"]
)


class LoginRequest(BaseModel):
    email: str
    password: str


class LogoutResponse(BaseModel):
    message: str


@router.post("")
def login(
    body: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    user = db.query(User).filter(User.email == body.email).first()

    if not user or not verify_password(body.password, user.password):
        log_security(
            db,
            "login_failed",
            user_id=user.id if user else None,
            description=f"Failed login attempt for {body.email}",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = create_access_token({"sub": str(user.id)})

    log_security(
        db,
        "login",
        user_id=user.id,
        description=f"Successful login for {user.email}",
        ip_address=ip_address,
        user_agent=user_agent,
    )

    log_audit(
        db,
        user.id,
        "login",
        "auth",
        user.id,
        f"User '{user.email}' logged in successfully",
        ip_address=ip_address,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
        },
    }


@router.post("/logout", response_model=LogoutResponse)
def logout(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ip_address = request.client.host if request.client else None

    log_security(
        db,
        "logout",
        user_id=current_user.id,
        description=f"User '{current_user.email}' logged out",
        ip_address=ip_address,
    )

    log_audit(
        db,
        current_user.id,
        "logout",
        "auth",
        current_user.id,
        f"User '{current_user.email}' logged out",
        ip_address=ip_address,
    )

    return {"message": "Logged out successfully"}
