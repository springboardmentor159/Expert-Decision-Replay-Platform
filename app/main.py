from datetime import timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, get_user_by_email, oauth2_scheme
from app.core.config import settings
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import (
    Token,
    UserCreate,
    UserResponse,
    Role,
)
from routers.decision import router as decisions_router
from routers.alternative import router as alternatives_router, decision_router as decision_alternatives_router
from routers.comments import router as comments_router
from routers.discussion_thread import router as discussion_thread_router
from routers.meeting_note import router as meeting_note_router

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)

# Include routers
app.include_router(decisions_router)
app.include_router(alternatives_router)
app.include_router(decision_alternatives_router)
app.include_router(comments_router)
app.include_router(discussion_thread_router)
app.include_router(meeting_note_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
    }


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


@app.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users", response_model=list[UserResponse])
def get_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User(
        full_name=user.full_name,
        email=str(user.email),
        role=user.role.value,
        employee_id=user.employee_id,
        department=user.department,
        designation=user.designation,
        phone_number=user.phone_number,
        password=hash_password(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user