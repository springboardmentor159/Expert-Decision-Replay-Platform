from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_decision_flow_requires_auth_and_uses_jwt_user():
    client = TestClient(app)
    unique_email = f"decision_user_{uuid4().hex}@example.com"

    user_payload = {
        "full_name": "Decision User",
        "email": unique_email,
        "role": "Administrator",
        "employee_id": "D12345",
        "department": "Engineering",
        "designation": "Lead Engineer",
        "phone_number": "+1234567890",
        "password": "super-secret",
    }

    create_user_response = client.post("/users", json=user_payload)
    assert create_user_response.status_code == 201
    created_user = create_user_response.json()

    login_response = client.post(
        "/token",
        data={"username": unique_email, "password": "super-secret"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    unauthorized_post = client.post(
        "/decisions",
        json={
            "title": "Move to PostgreSQL",
            "problem_statement": "Our current database does not support the required relational queries.",
            "category": "Technology",
        },
    )
    assert unauthorized_post.status_code == 401

    create_response = client.post(
        "/decisions",
        json={
            "title": "Move to PostgreSQL",
            "problem_statement": "Our current database does not support the required relational queries.",
            "category": "Technology",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == 201
    decision = create_response.json()
    assert decision["title"] == "Move to PostgreSQL"
    assert decision["category"] == "Technology"
    assert decision["status"] == "Draft"
    assert decision["created_by"] == created_user["id"]

    all_decisions = client.get("/decisions", headers={"Authorization": f"Bearer {token}"})
    assert all_decisions.status_code == 200
    assert len(all_decisions.json()) >= 1

    fetched_decision = client.get(
        f"/decisions/{decision['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert fetched_decision.status_code == 200
    assert fetched_decision.json()["id"] == decision["id"]

    missing_decision = client.get(
        "/decisions/999999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert missing_decision.status_code == 404
    assert "not found" in missing_decision.json()["detail"].lower()
