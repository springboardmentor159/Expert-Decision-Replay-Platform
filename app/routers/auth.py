from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import verify_password, create_access_token
from app.db.database import get_db
from app.models.user import User
from app.schemas.audit_log import AuditAction, AuditEntityType
from app.services.audit_service import log_audit


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

    client_ip = (
        request.client.host
        if request.client
        else None
    )

    if not user or not verify_password(
        form_data.password,
        user.password
    ):
        # Do not create a user-linked audit record here because
        # authentication failed and the user may not exist.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    log_audit(
        db=db,
        user_id=user.id,
        action=AuditAction.LOGIN,
        entity_type=AuditEntityType.USER,
        entity_id=user.id,
        description=f"User {user.id} logged in successfully",
        ip_address=client_ip,
        request_method="POST",
        endpoint="/auth/login"
    )

    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }