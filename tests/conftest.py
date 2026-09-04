import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.database import get_db, SessionLocal
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.services.security import hash_password, create_access_token


@pytest.fixture(scope="session")
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture(scope="session")
def test_org(db_session: Session):
    org = db_session.query(Organization).filter(Organization.name == "Integration Test Org").first()
    if not org:
        org = Organization(name="Integration Test Org", description="Test Organization for Integration Testing")
        db_session.add(org)
        db_session.commit()
        db_session.refresh(org)
    return org


def create_or_get_user(db: Session, email: str, full_name: str, role: UserRole, org_id: int, department: str = "Engineering"):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            full_name=full_name,
            role=role,
            password=hash_password("Password123!"),
            employee_id=f"EMP-{uuid.uuid4().hex[:6].upper()}",
            department=department,
            designation=f"{role.value} Specialist",
            phone_number="+1234567890",
            organization_id=org_id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_auth_headers_for_user(user: User):
    token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role.value}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session")
def employee_user(db_session: Session, test_org: Organization):
    return create_or_get_user(
        db_session, "integration_emp@test.com", "Test Employee", UserRole.EMPLOYEE, test_org.id, "Engineering"
    )


@pytest.fixture(scope="session")
def reviewer_user(db_session: Session, test_org: Organization):
    return create_or_get_user(
        db_session, "integration_rev@test.com", "Test Reviewer", UserRole.REVIEWER, test_org.id, "Quality Assurance"
    )


@pytest.fixture(scope="session")
def manager_user(db_session: Session, test_org: Organization):
    return create_or_get_user(
        db_session, "integration_mgr@test.com", "Test Manager", UserRole.MANAGER, test_org.id, "Engineering"
    )


@pytest.fixture(scope="session")
def admin_user(db_session: Session, test_org: Organization):
    return create_or_get_user(
        db_session, "integration_admin@test.com", "Test Administrator", UserRole.ADMINISTRATOR, test_org.id, "Operations"
    )


@pytest.fixture(scope="session")
def employee_headers(employee_user: User):
    return get_auth_headers_for_user(employee_user)


@pytest.fixture(scope="session")
def reviewer_headers(reviewer_user: User):
    return get_auth_headers_for_user(reviewer_user)


@pytest.fixture(scope="session")
def manager_headers(manager_user: User):
    return get_auth_headers_for_user(manager_user)


@pytest.fixture(scope="session")
def admin_headers(admin_user: User):
    return get_auth_headers_for_user(admin_user)
