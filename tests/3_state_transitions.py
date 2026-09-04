import uuid
from fastapi.testclient import TestClient


def test_valid_and_invalid_state_transitions(client: TestClient, employee_headers: dict):
    """
    Test state transitions as specified in Sprint 13 Section 8:
    - Draft -> Under Review: Valid
    - Under Review -> Approved: Valid
    - Approved -> Archived: Valid
    - Archived -> Draft: Invalid (400 Bad Request)
    - Draft -> Approved (skipping review): Invalid (400 Bad Request)
    - Modifying archived decision: Blocked with 400 Bad Request
    """
    unique_id = uuid.uuid4().hex[:6]

    # 1. Create Decision in Draft
    res = client.post(
        "/decisions",
        json={
            "title": f"State Transition Test {unique_id}",
            "problem_statement": "Verifying finite state machine transition rules.",
            "category": "Architecture",
        },
        headers=employee_headers,
    )
    assert res.status_code == 201
    dec_id = res.json()["id"]

    # 2. Invalid Transition: Draft -> Approved directly
    res = client.patch(
        f"/decisions/{dec_id}/status",
        json={"status": "Approved"},
        headers=employee_headers,
    )
    assert res.status_code == 400
    assert "Invalid state transition" in res.json()["detail"]

    # 3. Valid Transition: Draft -> Under Review
    res = client.patch(
        f"/decisions/{dec_id}/status",
        json={"status": "Under Review"},
        headers=employee_headers,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "Under Review"

    # 4. Valid Transition: Under Review -> Approved
    res = client.patch(
        f"/decisions/{dec_id}/status",
        json={"status": "Approved"},
        headers=employee_headers,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "Approved"

    # 5. Valid Transition: Approved -> Archived
    res = client.patch(
        f"/decisions/{dec_id}/status",
        json={"status": "Archived"},
        headers=employee_headers,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "Archived"

    # 6. Invalid Transition: Archived -> Draft
    res = client.patch(
        f"/decisions/{dec_id}/status",
        json={"status": "Draft"},
        headers=employee_headers,
    )
    assert res.status_code == 400
    assert "Cannot modify an archived decision" in res.json()["detail"] or "Invalid state transition" in res.json()["detail"]

    # 7. Immutability of Archived Decision
    res = client.put(
        f"/decisions/{dec_id}",
        json={
            "title": "Attempted Edit On Archived",
            "problem_statement": "Should be rejected.",
            "category": "Architecture",
        },
        headers=employee_headers,
    )
    assert res.status_code == 400
    assert "Cannot modify an archived decision" in res.json()["detail"]
