from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.utils.security import verify_password, hash_password
from app.utils.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── OAuth2 form-based login (Swagger Authorize button compatible) ─────────────
@router.post(
    "/token",
    summary="Login via OAuth2 form (use for Swagger Authorize 🔒)"
)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Accepts email as 'username'. Returns a Bearer JWT.
    Use this with the Swagger Authorize button."""
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=user.email,
        expires_delta=timedelta(minutes=60)
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ── JSON body login (integrated from Jamuna Rani) ─────────────────────────────
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login via JSON body"
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Accepts JSON body with email and password. Returns a Bearer JWT."""
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        subject=user.email,
        expires_delta=timedelta(minutes=60)
    )
    return {"access_token": access_token, "token_type": "bearer"}
