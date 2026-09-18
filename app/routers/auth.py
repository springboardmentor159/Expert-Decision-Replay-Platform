from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.database import get_db
from app.models.user import User
from app.schemas.audit_log import AuditAction, AuditEntityType
from app.schemas.user import UserRegistration, UserResponse
from app.services.audit_service import log_audit


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserRegistration,
    db: Session = Depends(get_db),
):
    """Public registration creates a standard Employee account.

    Privileged roles are assigned by authenticated administrators through
    the user-management endpoints.
    """
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    existing_employee = db.query(User).filter(User.employee_id == user_data.employee_id).first()
    if existing_employee:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Employee ID already registered")

    new_user = User(
        full_name=user_data.full_name.strip(),
        email=user_data.email,
        role="Employee",
        password=hash_password(user_data.password),
        employee_id=user_data.employee_id.strip(),
        department=user_data.department.strip(),
        designation=user_data.designation.strip(),
        phone_number=user_data.phone_number.strip(),
    )
    db.add(new_user)
    db.flush()
    log_audit(db, new_user.id, AuditAction.CREATE, AuditEntityType.USER, new_user.id, "Employee account registered", new_value={"email": new_user.email, "role": new_user.role}, request_method="POST", endpoint="/auth/register")
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    client_ip = (
        request.client.host
        if request.client
        else None
    )

    if not user or not verify_password(
        form_data.password,
        user.password
    ):
        # Do not create a user-linked audit record here because
        # authentication failed and the user may not exist.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    log_audit(
        db=db,
        user_id=user.id,
        action=AuditAction.LOGIN,
        entity_type=AuditEntityType.USER,
        entity_id=user.id,
        description=f"User {user.id} logged in successfully",
        ip_address=client_ip,
        request_method="POST",
        endpoint="/auth/login"
    )

    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }