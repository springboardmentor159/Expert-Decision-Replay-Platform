from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
    }


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
            status_code=400,
            detail="Email already registered",
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