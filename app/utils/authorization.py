from fastapi import HTTPException, status


def check_authorization(current_user: dict, required_role: str = None, allowed_roles: list = None):
    """
    Check if the current user has the required role for authorization.
    
    Args:
        current_user: The current authenticated user from JWT
        required_role: Single required role (e.g., "Administrator")
        allowed_roles: List of allowed roles (e.g., ["Administrator", "Manager"])
    
    Returns:
        Boolean indicating if user is authorized
        
    Raises:
        HTTPException: 403 Forbidden if user is not authorized
    """
    user_role = current_user.get("role")
    
    if required_role:
        if user_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Only {required_role} can access this resource"
            )
    elif allowed_roles:
        if user_role not in allowed_roles:
            allowed = ", ".join(allowed_roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Only users with roles [{allowed}] can access this resource"
            )
    
    return True
