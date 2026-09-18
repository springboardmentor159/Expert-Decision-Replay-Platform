from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.security import hash_password
from app.db.database import get_db
from app.models.user import User
from app.schemas.audit_log import AuditAction, AuditEntityType
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.activity_service import log_activity
from app.services.audit_service import log_audit


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


VALID_ROLES = {
    "Employee",
    "Reviewer",
    "Manager",
    "Administrator",
}


def require_admin(current_user: User) -> None:
    if current_user.role != "Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required"
        )


def clean_required(value: str, field_name: str) -> str:
    cleaned = value.strip()

    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{field_name} cannot be empty"
        )

    return cleaned


def clean_optional(value: str | None) -> str | None:
    if value is None:
        return None

    cleaned = value.strip()

    if not cleaned:
        return None

    return cleaned


def normalize_email(email: str) -> str:
    return email.strip().lower()


def ensure_user_scope(
    target_user: User,
    current_user: User
) -> None:
    if current_user.id == target_user.id:
        return

    if current_user.role == "Administrator":
        return

    if (
        current_user.role == "Manager"
        and current_user.department == target_user.department
    ):
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    email = normalize_email(user.email)
    employee_id = clean_required(
        user.employee_id,
        "Employee ID"
    )

    if (
        db.query(User)
        .filter(User.email == email)
        .first()
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    if (
        db.query(User)
        .filter(User.employee_id == employee_id)
        .first()
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee ID already registered"
        )

    new_user = User(
        full_name=clean_required(
            user.full_name,
            "Full name"
        ),
        email=email,
        role=user.role,
        password=hash_password(user.password),
        employee_id=employee_id,
        department=clean_required(
            user.department,
            "Department"
        ),
        designation=clean_required(
            user.designation,
            "Designation"
        ),
        phone_number=clean_required(
            user.phone_number,
            "Phone number"
        ),
    )

    db.add(new_user)
    db.flush()

    log_audit(
        db,
        current_user.id,
        AuditAction.CREATE,
        AuditEntityType.USER,
        new_user.id,
        f"Administrator created user {new_user.id}",
        new_value={
            "email": new_user.email,
            "role": new_user.role,
        },
        request_method="POST",
        endpoint="/users",
    )

    log_activity(
        db,
        current_user.id,
        "User Created",
        "User",
        new_user.id,
        f"User {new_user.id} created"
    )

    db.commit()
    db.refresh(new_user)

    return new_user


@router.get(
    "",
    response_model=List[UserResponse]
)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    valid_role_filter = User.role.in_(VALID_ROLES)

    if current_user.role == "Administrator":
        return (
            db.query(User)
            .filter(valid_role_filter)
            .order_by(User.full_name.asc())
            .all()
        )

    if current_user.role == "Manager":
        return (
            db.query(User)
            .filter(
                User.department == current_user.department,
                valid_role_filter,
            )
            .order_by(User.full_name.asc())
            .all()
        )

    if current_user.role in VALID_ROLES:
        return [current_user]

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Unsupported user role"
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.role.in_(VALID_ROLES),
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    ensure_user_scope(user, current_user)

    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    is_admin = current_user.role == "Administrator"

    if current_user.id != user_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    if user_data.role is not None and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can change user roles"
        )

    if user_data.email is not None:
        email = normalize_email(user_data.email)

        existing = (
            db.query(User)
            .filter(
                User.email == email,
                User.id != user_id
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        user.email = email

    if user_data.employee_id is not None:
        employee_id = clean_required(
            user_data.employee_id,
            "Employee ID"
        )

        existing = (
            db.query(User)
            .filter(
                User.employee_id == employee_id,
                User.id != user_id
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee ID already registered"
            )

        user.employee_id = employee_id

    if user_data.full_name is not None:
        user.full_name = clean_required(
            user_data.full_name,
            "Full name"
        )

    if user_data.department is not None:
        user.department = clean_required(
            user_data.department,
            "Department"
        )

    if user_data.designation is not None:
        user.designation = clean_required(
            user_data.designation,
            "Designation"
        )

    if user_data.phone_number is not None:
        user.phone_number = clean_required(
            user_data.phone_number,
            "Phone number"
        )

    if user_data.role is not None:
        user.role = user_data.role

    log_audit(
        db,
        current_user.id,
        AuditAction.UPDATE,
        AuditEntityType.USER,
        user.id,
        f"User {user.id} profile updated",
        request_method="PUT",
        endpoint=f"/users/{user.id}",
    )

    log_activity(
        db,
        current_user.id,
        "User Updated",
        "User",
        user.id,
        f"User {user.id} profile updated"
    )

    db.commit()
    db.refresh(user)

    return user


@router.delete(
    "/{user_id}"
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own administrator account"
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    log_audit(
        db,
        current_user.id,
        AuditAction.DELETE,
        AuditEntityType.USER,
        user.id,
        f"User {user.id} deleted",
        old_value={
            "email": user.email,
            "role": user.role,
        },
        request_method="DELETE",
        endpoint=f"/users/{user.id}",
    )

    log_activity(
        db,
        current_user.id,
        "User Deleted",
        "User",
        user.id,
        f"User {user.id} deleted"
    )

    db.delete(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This user cannot be deleted because other "
                "records still reference the account"
            )
        )

    return {
        "message": "User deleted successfully",
        "user_id": user_id
    }