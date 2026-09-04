import uuid
from fastapi.testclient import TestClient
from app.models.organization import Organization
from app.models.user import User


def test_user_registration(client: TestClient, test_org: Organization):
    """Test user registration for all 4 roles."""
    unique_suffix = uuid.uuid4().hex[:6]
    for role_name in ["Employee", "Reviewer", "Manager", "Administrator"]:
        reg_payload = {
            "full_name": f"Reg User {role_name}",
            "email": f"reg_{role_name.lower()}_{unique_suffix}@test.com",
            "password": "SecurePassword123!",
            "role": role_name,
            "employee_id": f"EMP-{role_name[:3].upper()}-{unique_suffix}",
            "department": "Engineering",
            "designation": f"{role_name} Associate",
            "phone_number": "+1987654321",
            "organization_id": test_org.id,
        }
        res = client.post("/auth/register", json=reg_payload)
        assert res.status_code == 201, f"Failed to register {role_name}: {res.text}"
        data = res.json()
        assert data["email"] == reg_payload["email"]
        assert data["role"] == role_name
        assert "password" not in data, "Password must never be returned in API response"


def test_auth_login_valid_and_invalid(client: TestClient, employee_user: User):
    """Test authentication with valid and invalid credentials."""
    # Valid login
    res = client.post(
        "/auth/login",
        data={"username": employee_user.email, "password": "Password123!"},
    )
    assert res.status_code == 200
    token_data = res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # Invalid password
    res = client.post(
        "/auth/login",
        data={"username": employee_user.email, "password": "WrongPassword!"},
    )
    assert res.status_code == 401
    assert "Invalid email or password" in res.json()["detail"]

    # Non-existent user
    res = client.post(
        "/auth/login",
        data={"username": "nonexistent_user@test.com", "password": "Password123!"},
    )
    assert res.status_code == 401

    # Missing credentials (Validation error 422)
    res = client.post("/auth/login", data={})
    assert res.status_code == 422


def test_user_profile_get_me(client: TestClient, employee_headers: dict, employee_user: User):
    """Test retrieving authenticated user profile via /auth/me."""
    res = client.get("/auth/me", headers=employee_headers)
    assert res.status_code == 200
    me = res.json()
    assert me["email"] == employee_user.email
    assert me["role"] == "Employee"
    assert "password" not in me


def test_unauthenticated_protected_endpoint(client: TestClient):
    """Accessing protected endpoints without valid JWT must return 401."""
    # Missing JWT
    res = client.get("/auth/me")
    assert res.status_code == 401

    # Invalid JWT
    res = client.get("/auth/me", headers={"Authorization": "Bearer invalid.jwt.token"})
    assert res.status_code == 401


def test_rbac_permission_matrix(
    client: TestClient,
    employee_headers: dict,
    reviewer_headers: dict,
    manager_headers: dict,
    admin_headers: dict,
):
    """
    Verify RBAC restrictions:
    - Organization Audit Logs (/audit-logs): Admin only. Employee, Reviewer, Manager -> 403 Forbidden
    - Security Logs (/security-logs): Admin only.
    - Access Logs (/access-logs): Admin only.
    - Admin Dashboard (/dashboard/admin): Admin only.
    """
    for h, role in [(employee_headers, "Employee"), (reviewer_headers, "Reviewer"), (manager_headers, "Manager")]:
        res_audit = client.get("/audit-logs", headers=h)
        assert res_audit.status_code == 403, f"{role} should be forbidden from /audit-logs, got {res_audit.status_code}"

        res_sec = client.get("/security-logs", headers=h)
        assert res_sec.status_code == 403, f"{role} should be forbidden from /security-logs, got {res_sec.status_code}"

        res_acc = client.get("/access-logs", headers=h)
        assert res_acc.status_code == 403, f"{role} should be forbidden from /access-logs, got {res_acc.status_code}"

        res_admin_dash = client.get("/dashboard/admin", headers=h)
        assert res_admin_dash.status_code == 403, f"{role} should be forbidden from /dashboard/admin, got {res_admin_dash.status_code}"

    # Admin access succeeds
    res_admin_audit = client.get("/audit-logs", headers=admin_headers)
    assert res_admin_audit.status_code == 200

    res_admin_sec = client.get("/security-logs", headers=admin_headers)
    assert res_admin_sec.status_code == 200

    res_admin_dash = client.get("/dashboard/admin", headers=admin_headers)
    assert res_admin_dash.status_code == 200
