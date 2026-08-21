from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import hash_password
from app.core.auth import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# --------------------------------------------------
# CREATE USER
# POST /users/
# --------------------------------------------------
@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    if user.employee_id:
        existing_employee = db.query(User).filter(
            User.employee_id == user.employee_id
        ).first()

        if existing_employee:
            raise HTTPException(
                status_code=400,
                detail="Employee ID already exists"
            )

    hashed_password = hash_password(user.password)

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role.value,
        employee_id=user.employee_id,
        department=user.department,
        designation=user.designation,
        phone_number=user.phone_number
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# --------------------------------------------------
# GET ALL USERS - PROTECTED
# GET /users/
# --------------------------------------------------
@router.get("/", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(User).all()


# --------------------------------------------------
# GET USER BY ID - PROTECTED
# GET /users/{user_id}
# --------------------------------------------------
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# --------------------------------------------------
# UPDATE USER - PROTECTED
# PUT /users/{user_id}
# --------------------------------------------------
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    existing_email = db.query(User).filter(
        User.email == user_data.email,
        User.id != user_id
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    if user_data.employee_id:
        existing_employee = db.query(User).filter(
            User.employee_id == user_data.employee_id,
            User.id != user_id
        ).first()

        if existing_employee:
            raise HTTPException(
                status_code=400,
                detail="Employee ID already exists"
            )

    user.full_name = user_data.full_name
    user.email = user_data.email
    user.role = user_data.role.value
    user.employee_id = user_data.employee_id
    user.department = user_data.department
    user.designation = user_data.designation
    user.phone_number = user_data.phone_number

    user.hashed_password = hash_password(user_data.password)

    db.commit()
    db.refresh(user)

    return user


# --------------------------------------------------
# DELETE USER - PROTECTED
# DELETE /users/{user_id}
# --------------------------------------------------
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }