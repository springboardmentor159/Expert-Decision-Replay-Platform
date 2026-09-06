import db

from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from routers import audit
from routers import decision
from routers import comment
from routers import alternative
from routers import discussion_thread
from routers import meeting_note
from routers import tags
from routers import dashboard
from routers import approval
from routers import activities

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.core.audit_logger import create_audit_log
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.models.security_log import SecurityLog
from app.models.access_log import AccessLog


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)


# =========================================================
# INCLUDE ROUTERS
# =========================================================

app.include_router(decision.router)
app.include_router(comment.router)
app.include_router(alternative.router)
app.include_router(discussion_thread.router)
app.include_router(meeting_note.router)
app.include_router(tags.router)
app.include_router(dashboard.router)
app.include_router(approval.router)
app.include_router(activities.router)
app.include_router(audit.router)


# =========================================================
# BEARER TOKEN SECURITY
# =========================================================

security = HTTPBearer()


# =========================================================
# AUTOMATIC ACCESS LOGGING
# =========================================================

@app.middleware("http")
async def access_log_middleware(request: Request, call_next):
    response = None

    try:
        response = await call_next(request)

        # -------------------------------------------------
        # Get user ID from JWT token if available
        # -------------------------------------------------

        user_id = None

        authorization = request.headers.get("Authorization")

        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ", 1)[1]

            try:
                payload = jwt.decode(
                    token,
                    settings.secret_key,
                    algorithms=[settings.algorithm],
                )

                user_id = payload.get("sub")

                if user_id is not None:
                    user_id = int(user_id)

            except (JWTError, ValueError, TypeError):
                user_id = None

        # -------------------------------------------------
        # Create Access Log
        # -------------------------------------------------

        db_generator = get_db()
        db_session = next(db_generator)

        try:
            access_log = AccessLog(
                user_id=user_id,
                request_method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                ip_address=(
                    request.client.host
                    if request.client
                    else None
                ),
            )

            db_session.add(access_log)
            db_session.commit()

        finally:
            db_generator.close()

        return response

    except Exception:
        raise


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
    }


# =========================================================
# CREATE USER
# =========================================================

@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.email == str(user.email))
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    existing_employee = (
        db.query(User)
        .filter(User.employee_id == user.employee_id)
        .first()
    )

    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee ID already registered",
        )

    db_user = User(
        full_name=user.full_name,
        employee_id=user.employee_id,
        email=str(user.email),
        department=user.department,
        designation=user.designation,
        phone_number=user.phone_number,
        role=user.role,
        password=hash_password(user.password),
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# =========================================================
# LOGIN
# =========================================================

@app.post("/login")
def login(
    email: str,
    password: str,
    request: Request,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    # -----------------------------------------------------
    # FAILED LOGIN - USER NOT FOUND
    # -----------------------------------------------------

    if not user:

        security_log = SecurityLog(
            user_id=None,
            event_type="LOGIN_FAILED",
            description="Failed login attempt",
            ip_address=(
                request.client.host
                if request.client
                else None
            ),
            request_method=request.method,
            endpoint=request.url.path,
        )

        db.add(security_log)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # -----------------------------------------------------
    # FAILED LOGIN - WRONG PASSWORD
    # -----------------------------------------------------

    if not verify_password(password, user.password):

        security_log = SecurityLog(
            user_id=user.id,
            event_type="LOGIN_FAILED",
            description="Failed login attempt",
            ip_address=(
                request.client.host
                if request.client
                else None
            ),
            request_method=request.method,
            endpoint=request.url.path,
        )

        db.add(security_log)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # -----------------------------------------------------
    # CREATE ACCESS TOKEN
    # -----------------------------------------------------

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": (
                user.role.value
                if hasattr(user.role, "value")
                else user.role
            ),
        }
    )

    # =====================================================
    # AUTOMATIC LOGIN AUDIT LOG
    # =====================================================

    create_audit_log(
        db=db,
        user_id=user.id,
        action="LOGIN",
        entity_type="User",
        entity_id=user.id,
        description="User logged in successfully",
        ip_address=(
            request.client.host
            if request.client
            else None
        ),
        request_method=request.method,
        endpoint=request.url.path,
    )

    # =====================================================
    # SECURITY LOG - LOGIN SUCCESS
    # =====================================================

    security_log = SecurityLog(
        user_id=user.id,
        event_type="LOGIN_SUCCESS",
        description="User logged in successfully",
        ip_address=(
            request.client.host
            if request.client
            else None
        ),
        request_method=request.method,
        endpoint=request.url.path,
    )

    db.add(security_log)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# =========================================================
# GET CURRENT USER PROFILE
# =========================================================

@app.get("/users/me")
def get_my_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        user_id = int(user_id)

    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return {
        "id": user.id,
        "full_name": user.full_name,
        "employee_id": user.employee_id,
        "email": user.email,
        "department": user.department,
        "designation": user.designation,
        "phone_number": user.phone_number,
        "role": (
            user.role.value
            if hasattr(user.role, "value")
            else user.role
        ),
    }


# =========================================================
# LOGOUT
# =========================================================

@app.post("/logout")
def logout(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        user_id = int(user_id)

    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    security_log = SecurityLog(
        user_id=user.id,
        event_type="LOGOUT",
        description="User logged out successfully",
        ip_address=(
            request.client.host
            if request.client
            else None
        ),
        request_method=request.method,
        endpoint=request.url.path,
    )

    db.add(security_log)
    db.commit()

    return {
        "message": "Logout successful"
    }