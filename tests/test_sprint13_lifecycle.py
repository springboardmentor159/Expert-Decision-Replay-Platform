from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_authenticated_user(role: str = "Employee") -> tuple[dict, dict]:
    password = "sprint13-password"
    payload = {
        "full_name": f"Sprint 13 {role}",
        "email": f"sprint13-{role.lower()}-{uuid4().hex}@example.com",
        "role": role,
        "employee_id": uuid4().hex[:8],
        "department": "Engineering",
        "designation": role,
        "phone_number": "+1234567890",
        "password": password,
    }
    response = client.post("/users", json=payload)
    assert response.status_code == 201

    login = client.post(
        "/auth/login",
        data={"username": payload["email"], "password": password},
    )
    assert login.status_code == 200
    return response.json(), {"Authorization": f"Bearer {login.json()['access_token']}"}


def create_decision(headers: dict) -> dict:
    response = client.post(
        "/decisions",
        headers=headers,
        json={
            "title": "Sprint 13 lifecycle decision",
            "problem_statement": "Validate decision state and access rules",
            "category": "Technology",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_decision_owner_and_role_authorization():
    owner, owner_headers = create_authenticated_user()
    _, other_headers = create_authenticated_user()
    decision = create_decision(owner_headers)

    response = client.put(
        f"/decisions/{decision['id']}",
        headers=other_headers,
        json={"title": "Unauthorized update"},
    )
    assert response.status_code == 403


def test_decision_status_transitions_are_enforced():
    _, headers = create_authenticated_user()
    decision = create_decision(headers)

    invalid = client.patch(
        f"/decisions/{decision['id']}/status",
        headers=headers,
        json={"status": "Approved"},
    )
    assert invalid.status_code == 409

    under_review = client.patch(
        f"/decisions/{decision['id']}/status",
        headers=headers,
        json={"status": "Under Review"},
    )
    assert under_review.status_code == 200

    archived = client.delete(f"/decisions/{decision['id']}", headers=headers)
    assert archived.status_code == 204

    invalid_after_archive = client.patch(
        f"/decisions/{decision['id']}/status",
        headers=headers,
        json={"status": "Draft"},
    )
    assert invalid_after_archive.status_code == 409
