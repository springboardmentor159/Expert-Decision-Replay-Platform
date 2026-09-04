from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse
)
from app.services.auth import get_current_user
from app.services.authorization import require_roles
from app.services.security import hash_password


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# CREATE USER
# Administrator only
@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMINISTRATOR)
    )
):
    # Verify organization exists
    organization = (
        db.query(Organization)
        .filter(
            Organization.id == user.organization_id
        )
        .first()
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Check duplicate email
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check duplicate employee ID
    if user.employee_id:
        existing_employee = (
            db.query(User)
            .filter(
                User.employee_id == user.employee_id
            )
            .first()
        )

        if existing_employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID already registered"
            )

    # Create user
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        role=user.role,
        password=hash_password(user.password),
        employee_id=user.employee_id,
        department=user.department,
        designation=user.designation,
        phone_number=user.phone_number,
        organization_id=user.organization_id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# GET ALL USERS
#
# Administrator:
#   Can see users from all organizations.
#
# Manager:
#   Can see users from their own organization only.
#
@router.get(
    "",
    response_model=List[UserResponse]
)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.MANAGER,
            UserRole.ADMINISTRATOR
        )
    )
):
    query = db.query(User)

    # Administrator can view all users
    if current_user.role == UserRole.ADMINISTRATOR:
        return query.all()

    # Manager can only view users
    # belonging to their organization
    return (
        query
        .filter(
            User.organization_id
            == current_user.organization_id
        )
        .all()
    )


# GET USER BY ID
#
# Users can view themselves.
#
# Managers:
#   Can view users in their organization.
#
# Administrators:
#   Can view anyone.
#
@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    # User can view their own profile
    if current_user.id == user_id:
        return user

    # Administrator can view anyone
    if current_user.role == UserRole.ADMINISTRATOR:
        return user

    # Managers can only view users
    # in their own organization
    if current_user.role == UserRole.MANAGER:
        if (
            user.organization_id
            != current_user.organization_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission to "
                    "view users from another organization"
                )
            )

        return user

    # Other roles cannot view another user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to view this user"
    )


# UPDATE USER
@router.put(
    "/{user_id}",
    response_model=UserResponse
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    # Determine whether this is the user's own profile
    is_own_profile = current_user.id == user_id

    # Organization access check
    if not is_own_profile:

        # Administrator can edit anyone
        if current_user.role == UserRole.ADMINISTRATOR:
            pass

        # Manager can edit users in same organization
        elif current_user.role == UserRole.MANAGER:

            if (
                user.organization_id
                != current_user.organization_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "You do not have permission to "
                        "edit users from another organization"
                    )
                )

        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission "
                    "to edit this user"
                )
            )

    # Organization change protection
    if user_data.organization_id is not None:

        # Only Administrator can change organization
        if current_user.role != UserRole.ADMINISTRATOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Only an Administrator can "
                    "change a user's organization"
                )
            )

        # Verify new organization exists
        organization = (
            db.query(Organization)
            .filter(
                Organization.id
                == user_data.organization_id
            )
            .first()
        )

        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        user.organization_id = user_data.organization_id

    # Role change protection
    if user_data.role is not None:

        # User cannot change their own role
        if is_own_profile:

            if user_data.role != current_user.role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You cannot change your own role"
                )

        # Only Administrator can change another user's role
        elif current_user.role != UserRole.ADMINISTRATOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Only an Administrator can "
                    "change user roles"
                )
            )

        user.role = user_data.role

    # Update full name
    if user_data.full_name is not None:
        user.full_name = user_data.full_name

    # Update email
    if user_data.email is not None:

        existing_user = (
            db.query(User)
            .filter(
                User.email == user_data.email,
                User.id != user_id
            )
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        user.email = user_data.email

    # Update employee ID
    if user_data.employee_id is not None:

        existing_employee = (
            db.query(User)
            .filter(
                User.employee_id
                == user_data.employee_id,
                User.id != user_id
            )
            .first()
        )

        if existing_employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID already registered"
            )

        user.employee_id = user_data.employee_id

    # Update department
    if user_data.department is not None:
        user.department = user_data.department

    # Update designation
    if user_data.designation is not None:
        user.designation = user_data.designation

    # Update phone number
    if user_data.phone_number is not None:
        user.phone_number = user_data.phone_number

    # Update password
    if user_data.password is not None:
        user.password = hash_password(
            user_data.password
        )

    db.commit()
    db.refresh(user)

    return user


# DELETE USER
# Administrator only
@router.delete(
    "/{user_id}"
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMINISTRATOR
        )
    )
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

    # Prevent Administrator from deleting own account
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }
