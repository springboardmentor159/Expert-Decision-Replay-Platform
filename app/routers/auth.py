from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.revoked_token import RevokedToken
from app.core.security import (
    verify_password,
    create_access_token,
    get_current_user,
    SECRET_KEY,
    ALGORITHM,
)
from app.services.security import create_security_log
from app.schemas.auth import TokenResponse


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

security = HTTPBearer()


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # ========================================================
    # FIND USER
    # ========================================================

    user = (
        db.query(User)
        .filter(User.email == form_data.username)
        .first()
    )

    # ========================================================
    # LOGIN FAILED - USER NOT FOUND
    # ========================================================

    if not user:
        create_security_log(
            db=db,
            event_type="LOGIN_FAILED",
            description="Login failed: invalid email or password",
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # ========================================================
    # CHECK PASSWORD
    # ========================================================

    if not verify_password(
        form_data.password,
        user.password,
    ):
        create_security_log(
            db=db,
            event_type="LOGIN_FAILED",
            description="Login failed: invalid email or password",
            user_id=user.id,
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # ========================================================
    # LOGIN SUCCESS
    # ========================================================

    create_security_log(
        db=db,
        event_type="LOGIN_SUCCESS",
        description=f"User {user.id} logged in successfully",
        user_id=user.id,
    )

    # ========================================================
    # CREATE JWT TOKEN
    # ========================================================

    access_token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
        }
    )

    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# ============================================================
# LOGOUT
# ============================================================

@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    token = credentials.credentials

    # ========================================================
    # DECODE CURRENT TOKEN TO GET JTI AND EXPIRATION
    # ========================================================

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        jti = payload.get("jti")
        exp = payload.get("exp")

        if not jti or not exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    # ========================================================
    # CHECK IF TOKEN IS ALREADY REVOKED
    # ========================================================

    existing_token = (
        db.query(RevokedToken)
        .filter(RevokedToken.jti == jti)
        .first()
    )

    if existing_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has already been revoked",
        )

    # ========================================================
    # STORE REVOKED TOKEN
    # ========================================================

    revoked_token = RevokedToken(
        jti=jti,
        user_id=current_user.id,
        expires_at=__import__("datetime").datetime.fromtimestamp(
            exp,
            tz=__import__("datetime").timezone.utc,
        ).replace(tzinfo=None),
    )

    db.add(revoked_token)

    # ========================================================
    # SECURITY LOG
    # ========================================================

    create_security_log(
        db=db,
        event_type="LOGOUT",
        description=f"User {current_user.id} logged out successfully",
        user_id=current_user.id,
    )

    db.commit()

    return {
        "message": "Logout successful"
    }