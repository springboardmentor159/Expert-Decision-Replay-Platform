from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import verify_password, create_access_token
from app.db.database import get_db
from app.models.user import User
from app.models.security_log import SecurityLog


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ============================================================
# LOGIN
# POST /auth/login
# ============================================================

@router.post("/login")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # GET USER
    # --------------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.email == form_data.username
        )
        .first()
    )

    # --------------------------------------------------------
    # FAILED LOGIN - USER NOT FOUND
    # --------------------------------------------------------

    if not user:

        security_log = SecurityLog(
            user_id=None,
            event_type="LOGIN_FAILED",
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

        db.add(security_log)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # --------------------------------------------------------
    # FAILED LOGIN - WRONG PASSWORD
    # --------------------------------------------------------

    if not verify_password(
        form_data.password,
        user.hashed_password
    ):

        security_log = SecurityLog(
            user_id=user.id,
            event_type="LOGIN_FAILED",
            description=(
                f"Failed login attempt for "
                f"User {user.id}"
            ),
            ip_address=(
                request.client.host
                if request.client
                else None
            )
        )

        db.add(security_log)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # --------------------------------------------------------
    # CREATE JWT TOKEN
    # --------------------------------------------------------

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role
        }
    )

    # --------------------------------------------------------
    # SUCCESSFUL LOGIN SECURITY LOG
    # --------------------------------------------------------

    security_log = SecurityLog(
        user_id=user.id,
        event_type="LOGIN_SUCCESS",
        description=(
            f"User {user.id} logged in successfully"
        ),
        ip_address=(
            request.client.host
            if request.client
            else None
        )
    )

    db.add(security_log)
    db.commit()

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }