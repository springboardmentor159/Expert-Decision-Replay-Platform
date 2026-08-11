"""
Test endpoints for verifying role-based and department-based authorization.

These endpoints are for testing ONLY. Do NOT use them for business logic.

Role test endpoints:
    GET /test/employee     → Employee only
    GET /test/reviewer     → Reviewer only
    GET /test/manager      → Manager only
    GET /test/admin        → Administrator only

Department test endpoints:
    GET /test/it           → IT department users only
    GET /test/cac          → CAC department users only

HTTP status codes:
    200 OK          → authenticated and authorized
    401 Unauthorized → missing / invalid / expired token
    403 Forbidden    → authenticated but wrong role or department
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import User
from app.utils.jwt import get_current_user

router = APIRouter(prefix="/test", tags=["Authorization Tests"])


# ─── Dependency factories ─────────────────────────────────────────────────────

def require_role(required_role: str):
    """Return a FastAPI dependency that enforces a specific role.

    Raises:
        401 if the user is not authenticated (handled by get_current_user)
        403 if the authenticated user's role does not match required_role
    """
    def _check_role(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}. "
                       f"Your role: {current_user.role}"
            )
        return current_user
    return _check_role


def require_department(required_department: str):
    """Return a FastAPI dependency that enforces a specific department.

    Raises:
        401 if the user is not authenticated (handled by get_current_user)
        403 if the authenticated user's department does not match required_department
    """
    def _check_department(current_user: User = Depends(get_current_user)) -> User:
        if current_user.department != required_department:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required department: {required_department}. "
                       f"Your department: {current_user.department}"
            )
        return current_user
    return _check_department


# ─── Role test endpoints ──────────────────────────────────────────────────────

@router.get(
    "/employee",
    summary="Employee-only endpoint",
    description="Accessible only to users with role = Employee"
)
def test_employee(current_user: User = Depends(require_role("Employee"))):
    return {
        "message": "Access granted",
        "user": current_user.full_name,
        "role": current_user.role,
        "department": current_user.department,
    }


@router.get(
    "/reviewer",
    summary="Reviewer-only endpoint",
    description="Accessible only to users with role = Reviewer"
)
def test_reviewer(current_user: User = Depends(require_role("Reviewer"))):
    return {
        "message": "Access granted",
        "user": current_user.full_name,
        "role": current_user.role,
        "department": current_user.department,
    }


@router.get(
    "/manager",
    summary="Manager-only endpoint",
    description="Accessible only to users with role = Manager"
)
def test_manager(current_user: User = Depends(require_role("Manager"))):
    return {
        "message": "Access granted",
        "user": current_user.full_name,
        "role": current_user.role,
        "department": current_user.department,
    }


@router.get(
    "/admin",
    summary="Administrator-only endpoint",
    description="Accessible only to users with role = Administrator"
)
def test_admin(current_user: User = Depends(require_role("Administrator"))):
    return {
        "message": "Access granted",
        "user": current_user.full_name,
        "role": current_user.role,
        "department": current_user.department,
    }


# ─── Department test endpoints ────────────────────────────────────────────────

@router.get(
    "/it",
    summary="IT department-only endpoint",
    description="Accessible only to authenticated users in the IT department"
)
def test_it(current_user: User = Depends(require_department("IT"))):
    return {
        "message": "Access granted",
        "user": current_user.full_name,
        "role": current_user.role,
        "department": current_user.department,
    }


@router.get(
    "/cac",
    summary="CAC department-only endpoint",
    description="Accessible only to authenticated users in the CAC department"
)
def test_cac(current_user: User = Depends(require_department("CAC"))):
    return {
        "message": "Access granted",
        "user": current_user.full_name,
        "role": current_user.role,
        "department": current_user.department,
    }
