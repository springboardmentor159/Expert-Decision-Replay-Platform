from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

from routers import decision


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)


# -------------------------
# Decision Router
# -------------------------

app.include_router(decision.router)


# -------------------------
# Bearer Token Security
# -------------------------

security = HTTPBearer()


# -------------------------
# Health Check
# -------------------------

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
    }


# -------------------------
# Create User
# -------------------------

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


# -------------------------
# Login
# -------------------------

@app.post("/login")
def login(
    email: str,
    password: str,
    db: Session = Depends(get_db),
):

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

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

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# -------------------------
# Protected API
# -------------------------

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