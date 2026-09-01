from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.user import User


# =========================================================
# BEARER SECURITY
# =========================================================

security = HTTPBearer()


# =========================================================
# GET CURRENT USER
# =========================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    # -----------------------------------------------------
    # Find user in PostgreSQL
    # -----------------------------------------------------

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


# =========================================================
# GET USER ROLE
# =========================================================

def get_user_role(user: User) -> str:
    """
    Return the user's role as a normal string.
    Supports both String and Enum-style role values.
    """

    return (
        user.role.value
        if hasattr(user.role, "value")
        else user.role
    )


# =========================================================
# ADMIN AUTHORIZATION
# =========================================================

def require_admin(
    current_user: User = Depends(get_current_user)
):
    role = get_user_role(current_user)

    if role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permission"
        )

    return current_user


# =========================================================
# MANAGER AUTHORIZATION
# =========================================================

def require_manager(
    current_user: User = Depends(get_current_user)
):
    role = get_user_role(current_user)

    if role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager permission required"
        )

    return current_user