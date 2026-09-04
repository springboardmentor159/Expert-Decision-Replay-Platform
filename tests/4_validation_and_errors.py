import uuid
from fastapi.testclient import TestClient


def test_validation_rules(client: TestClient, employee_headers: dict):
    """
    Test Validation Rules (Sprint 13 Section 9):
    - Missing required fields: 422
    - Invalid feasibility score (0 and 6): 422
    - Invalid risk level ('Very Dangerous'): 422
    - Invalid status: 422
    - Invalid email: 422
    - Invalid non-integer ID: 422
    """
    unique_id = uuid.uuid4().hex[:6]

    # Create base decision for sub-resource tests
    res = client.post(
        "/decisions",
        json={
            "title": f"Validation Test Decision {unique_id}",
            "problem_statement": "Validating schemas and inputs.",
            "category": "Technology",
        },
        headers=employee_headers,
    )
    assert res.status_code == 201
    dec_id = res.json()["id"]

    # 1. Missing required fields in decision
    res = client.post("/decisions", json={}, headers=employee_headers)
    assert res.status_code == 422

    # 2. Invalid Feasibility Score = 0
    res = client.post(
        f"/decisions/{dec_id}/alternatives",
        json={
            "name": "Alt Zero",
            "description": "desc",
            "pros": "pros",
            "cons": "cons",
            "estimated_cost": 100.0,
            "feasibility_score": 0,
            "risk_level": "Low",
        },
        headers=employee_headers,
    )
    assert res.status_code == 422, f"Expected 422 for feasibility=0, got {res.status_code}"

    # 3. Invalid Feasibility Score = 6
    res = client.post(
        f"/decisions/{dec_id}/alternatives",
        json={
            "name": "Alt Six",
            "description": "desc",
            "pros": "pros",
            "cons": "cons",
            "estimated_cost": 100.0,
            "feasibility_score": 6,
            "risk_level": "Low",
        },
        headers=employee_headers,
    )
    assert res.status_code == 422, f"Expected 422 for feasibility=6, got {res.status_code}"

    # 4. Invalid Risk Level = 'Very Dangerous'
    res = client.post(
        f"/decisions/{dec_id}/alternatives",
        json={
            "name": "Alt Risk",
            "description": "desc",
            "pros": "pros",
            "cons": "cons",
            "estimated_cost": 100.0,
            "feasibility_score": 3,
            "risk_level": "Very Dangerous",
        },
        headers=employee_headers,
    )
    assert res.status_code == 422, f"Expected 422 for invalid risk_level, got {res.status_code}"

    # 5. Invalid Decision Status
    res = client.patch(
        f"/decisions/{dec_id}/status",
        json={"status": "NonExistentStatus"},
        headers=employee_headers,
    )
    assert res.status_code == 422

    # 6. Invalid Email format on register
    res = client.post(
        "/auth/register",
        json={
            "full_name": "Bad Email",
            "email": "not-an-email",
            "password": "Password123!",
            "role": "Employee",
            "organization_id": 1,
        },
    )
    assert res.status_code == 422

    # 7. Invalid integer ID parameter (decision_id = abc)
    res = client.get("/decisions/abc", headers=employee_headers)
    assert res.status_code == 422


def test_error_handling_not_found(client: TestClient, employee_headers: dict):
    """
    Test Error Handling (Sprint 13 Section 10):
    - Non-existing Decision -> 404
    - Non-existing Alternative -> 404
    - Non-existing Approval -> 404
    - Non-existing User -> 404
    """
    res = client.get("/decisions/999999", headers=employee_headers)
    assert res.status_code == 404

    res = client.get("/alternatives/999999", headers=employee_headers)
    assert res.status_code == 404

    res = client.get("/approvals/999999", headers=employee_headers)
    assert res.status_code == 404

    res = client.get("/users/999999", headers=employee_headers)
    assert res.status_code == 404
