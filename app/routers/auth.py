from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.security_log import SecurityLog
from app.core.security import verify_password, create_access_token

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
    user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    client_ip = request.client.host if request.client else None

    if not user or not verify_password(
        form_data.password,
        user.password
    ):
        security_log = SecurityLog(
            user_id=user.id if user else None,
            event_type="LOGIN_FAILED",
            description="Failed login attempt",
            ip_address=client_ip
        )

        db.add(security_log)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role
        }
    )

    security_log = SecurityLog(
        user_id=user.id,
        event_type="LOGIN_SUCCESS",
        description="Successful login",
        ip_address=client_ip
    )

    db.add(security_log)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }