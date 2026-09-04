from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse
)
from app.utils.password import hash_password
from app.utils.security import security, verify_token


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# JWT AUTHENTICATION
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    return payload


# CREATE USER / REGISTER
@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
):
    current_user = verify_token(credentials.credentials) if credentials else None
    if user.role.value != "Employee" and (not current_user or current_user.get("role") != "Administrator"):
        raise HTTPException(status_code=403, detail="Only administrators can create privileged users")

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        role=user.role,
        password=hash_password(user.password),
        employee_id=user.employee_id,
        department=user.department,
        designation=user.designation,
        phone_number=user.phone_number
    )

    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email or employee ID already exists")
    db.refresh(new_user)

    return new_user


# GET ALL USERS - PROTECTED
@router.get(
    "",
    response_model=List[UserResponse]
)
def get_users(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(User).all()


# GET USER BY ID - PROTECTED
@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    is_admin = current_user.get("role") == "Administrator"
    if int(current_user["sub"]) != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="Users can only update their own profile")
    if user_data.role is not None and not is_admin:
        raise HTTPException(status_code=403, detail="Only administrators can change roles")

    return user


# UPDATE USER - PROTECTED
@router.put(
    "/{user_id}",
    response_model=UserResponse
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user_data.full_name is not None:
        user.full_name = user_data.full_name

    if user_data.email is not None:
        user.email = user_data.email

    if user_data.role is not None:
        user.role = user_data.role

    if user_data.password is not None:
        user.password = hash_password(user_data.password)

    if user_data.employee_id is not None:
        user.employee_id = user_data.employee_id

    if user_data.department is not None:
        user.department = user_data.department

    if user_data.designation is not None:
        user.designation = user_data.designation

    if user_data.phone_number is not None:
        user.phone_number = user_data.phone_number

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email or employee ID already exists")
    db.refresh(user)

    return user


# DELETE USER - PROTECTED
@router.delete(
    "/{user_id}"
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if current_user.get("role") != "Administrator":
        raise HTTPException(status_code=403, detail="Only administrators can delete users")

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }