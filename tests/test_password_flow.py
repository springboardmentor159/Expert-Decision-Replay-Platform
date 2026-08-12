from pathlib import Path
import sys

import pytest
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.security import hash_password, verify_password
from app.schemas.user import Role, UserCreate


def test_password_hashing_and_verification():
    password = "super-secret"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong-password", hashed)


def test_user_create_schema_accepts_profile_fields():
    user = UserCreate(
        full_name="Jane Doe",
        email="jane@example.com",
        role=Role.Administrator,
        employee_id="E12345",
        department="Engineering",
        designation="Senior Engineer",
        phone_number="+1234567890",
        password="super-secret",
    )

    assert user.password == "super-secret"
    assert user.role == Role.Administrator
    assert user.employee_id == "E12345"
    assert user.department == "Engineering"
    assert user.designation == "Senior Engineer"
    assert user.phone_number == "+1234567890"


def test_user_create_schema_rejects_invalid_role():
    with pytest.raises(ValidationError):
        UserCreate(
            full_name="Jane Doe",
            email="jane@example.com",
            role="admin",
            employee_id="E12345",
            department="Engineering",
            designation="Senior Engineer",
            phone_number="+1234567890",
            password="super-secret",
        )


def test_login_and_protected_users_endpoint():
    from fastapi.testclient import TestClient
    from app.main import app
    from uuid import uuid4

    client = TestClient(app)
    unique_email = f"user_{uuid4().hex}@example.com"
    create_payload = {
        "full_name": "Test User",
        "email": unique_email,
        "role": "Administrator",
        "employee_id": "E12345",
        "department": "Engineering",
        "designation": "Senior Engineer",
        "phone_number": "+1234567890",
        "password": "super-secret",
    }

    response = client.post("/users", json=create_payload)
    assert response.status_code == 201

    login_response = client.post(
        "/token",
        data={"username": unique_email, "password": "super-secret"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert token_data["token_type"] == "bearer"
    assert "access_token" in token_data

    bearer_token = token_data["access_token"]
    protected_response = client.get(
        "/users",
        headers={"Authorization": f"Bearer {bearer_token}"},
    )
    assert protected_response.status_code == 200
    assert isinstance(protected_response.json(), list)

    unauthorized_response = client.get("/users")
    assert unauthorized_response.status_code == 401
