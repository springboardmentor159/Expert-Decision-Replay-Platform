import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.database import get_db
from app.main import app

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_user_valid_roles_and_profile():
    # Test creating user with role 'Employee'
    user_data = {
        "full_name": "John Doe",
        "email": "john@example.com",
        "role": "Employee",
        "password": "Password123!",
        "employee_id": "EMP-001",
        "department": "Engineering",
        "designation": "Software Engineer",
        "phone_number": "+1234567890"
    }
    response = client.post("/users", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == "john@example.com"
    assert data["role"] == "Employee"
    assert data["employee_id"] == "EMP-001"
    assert data["department"] == "Engineering"
    assert data["designation"] == "Software Engineer"
    assert data["phone_number"] == "+1234567890"


def test_reject_invalid_role():
    user_data = {
        "full_name": "Jane Smith",
        "email": "jane@example.com",
        "role": "SuperAdmin",  # Invalid role!
        "password": "Password123!",
        "employee_id": "EMP-002"
    }
    response = client.post("/users", json=user_data)
    assert response.status_code == 422  # Unprocessable Entity (role validation failed)


def test_supported_roles():
    valid_roles = ["Employee", "Reviewer", "Manager", "Administrator"]
    for idx, role in enumerate(valid_roles):
        user_data = {
            "full_name": f"User {role}",
            "email": f"user_{role.lower()}@example.com",
            "role": role,
            "password": "Password123!",
            "employee_id": f"EMP-10{idx}"
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == 201
        assert response.json()["role"] == role


def test_login_and_jwt_token():
    # 1. Register user
    user_data = {
        "full_name": "Alice Manager",
        "email": "alice@example.com",
        "role": "Manager",
        "password": "SecretPassword123",
        "employee_id": "EMP-003"
    }
    reg_response = client.post("/users", json=user_data)
    assert reg_response.status_code == 201

    # 2. Login with valid credentials
    login_data = {
        "email": "alice@example.com",
        "password": "SecretPassword123"
    }
    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # Also test /users/login endpoint alias
    alias_response = client.post("/users/login", json=login_data)
    assert alias_response.status_code == 200
    assert "access_token" in alias_response.json()

    # 3. Login with invalid password
    invalid_login = {
        "email": "alice@example.com",
        "password": "WrongPassword"
    }
    bad_response = client.post("/auth/login", json=invalid_login)
    assert bad_response.status_code == 401


def test_protected_endpoints():
    # Create user and login
    user_data = {
        "full_name": "Bob Reviewer",
        "email": "bob@example.com",
        "role": "Reviewer",
        "password": "Password123!",
        "employee_id": "EMP-004"
    }
    client.post("/users", json=user_data)

    login_resp = client.post("/auth/login", json={"email": "bob@example.com", "password": "Password123!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Access protected GET /users without token -> 401
    assert client.get("/users").status_code == 401

    # 2. Access protected GET /users/me without token -> 401
    assert client.get("/users/me").status_code == 401

    # 3. Access protected GET /users with valid token -> 200
    res_users = client.get("/users", headers=headers)
    assert res_users.status_code == 200
    assert len(res_users.json()) == 1

    # 4. Access protected GET /users/me with valid token -> 200
    res_me = client.get("/users/me", headers=headers)
    assert res_me.status_code == 200
    assert res_me.json()["email"] == "bob@example.com"
    assert res_me.json()["role"] == "Reviewer"

    # 5. Access protected PUT /users/{id} with valid token -> 200
    user_id = res_me.json()["id"]
    update_data = {
        "department": "Quality Assurance",
        "designation": "Senior Reviewer"
    }
    res_update = client.put(f"/users/{user_id}", json=update_data, headers=headers)
    assert res_update.status_code == 200
    assert res_update.json()["department"] == "Quality Assurance"
    assert res_update.json()["designation"] == "Senior Reviewer"
