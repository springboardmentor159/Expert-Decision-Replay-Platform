from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.security_log import SecurityLog
from app.schemas.user import UserLogin
from app.schemas.token import Token
from app.core.security import (
    verify_password,
    create_access_token,
    get_current_user
)


router = APIRouter(tags=["Auth"])


@router.post("/login", response_model=Token)
def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == credentials.email
    ).first()

    ip_address = request.client.host if request.client else None

    # ==========================================
    # FAILED LOGIN
    # ==========================================
    if not user or not verify_password(
        credentials.password,
        user.hashed_password
    ):
        security_log = SecurityLog(
            user_id=user.id if user else None,
            event_type="LOGIN_FAILURE",
            description="Failed login attempt",
            ip_address=ip_address
        )

        db.add(security_log)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # ==========================================
    # SUCCESSFUL LOGIN
    # ==========================================
    security_log = SecurityLog(
        user_id=user.id,
        event_type="LOGIN_SUCCESS",
        description="User logged in successfully",
        ip_address=ip_address
    )

    db.add(security_log)
    db.commit()

    # ==========================================
    # CREATE JWT TOKEN
    # ==========================================
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


@router.post("/logout")
def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ip_address = request.client.host if request.client else None

    # ==========================================
    # LOGOUT SECURITY LOG
    # ==========================================
    security_log = SecurityLog(
        user_id=current_user.id,
        event_type="LOGOUT",
        description="User logged out",
        ip_address=ip_address
    )

    db.add(security_log)
    db.commit()

    return {
        "message": "Logout successful"
    }