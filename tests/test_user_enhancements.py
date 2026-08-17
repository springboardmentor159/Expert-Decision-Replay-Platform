import pytest
from datetime import timedelta
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.enums import UserRole
from app.core.security import hash_password


def test_registration_default_role(client):
    response = client.post("/users", json={
        "full_name": "Employee User",
        "email": "employee@example.com",
        "password": "password123",
        "employee_id": "EMP_DEFAULT"
    })
    assert response.status_code == 201
    body = response.json()
    assert body["role"] == "Employee"
    assert body["employee_id"] == "EMP_DEFAULT"


def test_registration_valid_roles(client):
    roles = ["Reviewer", "Manager", "Administrator"]
    for idx, role in enumerate(roles):
        response = client.post("/users", json={
            "full_name": f"{role} User",
            "email": f"{role.lower()}@example.com",
            "password": "password123",
            "employee_id": f"EMP_{role.upper()}",
            "role": role
        })
        assert response.status_code == 201
        body = response.json()
        assert body["role"] == role


def test_registration_invalid_role(client):
    response = client.post("/users", json={
        "full_name": "Invalid Role User",
        "email": "invalid_role@example.com",
        "password": "password123",
        "employee_id": "EMP_INVALID",
        "role": "Developer"  # Invalid role
    })
    assert response.status_code == 422


def test_protected_routes_without_token(client):
    endpoints = [
        ("GET", "/users"),
        ("GET", "/users/1"),
        ("PUT", "/users/1"),
        ("DELETE", "/users/1"),
    ]
    for method, path in endpoints:
        if method == "GET":
            response = client.get(path)
        elif method == "PUT":
            response = client.put(path, json={"full_name": "Updated"})
        elif method == "DELETE":
            response = client.delete(path)
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"


def test_protected_routes_with_invalid_token(client):
    headers = {"Authorization": "Bearer not-a-valid-token"}
    response = client.get("/users", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


def test_protected_routes_with_expired_token(client, make_token):
    token = make_token("1", expires_delta=timedelta(seconds=-5))
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


def test_protected_routes_with_valid_token(client, db_session, make_token):
    # Create user in DB
    user = User(
        full_name="Auth User",
        email="auth_user@example.com",
        role=UserRole.EMPLOYEE,
        password=hash_password("password123"),
        employee_id="EMP_AUTH"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = make_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/users", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body) >= 1
    assert any(u["email"] == "auth_user@example.com" for u in body)


def test_database_check_constraint(db_session):
    # Bypass Pydantic validation by creating model directly
    user = User(
        full_name="Bad Role User",
        email="bad_role@example.com",
        role="Developer",  # Invalid role
        password=hash_password("password123"),
        employee_id="EMP_BAD_DB"
    )
    db_session.add(user)
    
    with pytest.raises(IntegrityError):
        db_session.commit()
