from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_register_and_login_flow():
    register_payload = {
        "full_name": "Test User",
        "email": "test.user@example.com",
        "role": "Employee",
        "password": "StrongPass123!",
        "employee_id": "EMP-1001",
        "department": "Engineering",
        "designation": "Engineer",
        "phone_number": "5551234567",
    }

    register_response = client.post("/users", json=register_payload)
    assert register_response.status_code == 201, register_response.text

    login_response = client.post(
        "/auth/login",
        json={"email": "test.user@example.com", "password": "StrongPass123!"},
    )
    assert login_response.status_code == 200, login_response.text
    token = login_response.json()["access_token"]
    assert token

    protected_response = client.get(
        "/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert protected_response.status_code == 200
