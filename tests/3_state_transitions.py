import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.organization import Organization
from app.models.user import UserRole
from tests.conftest import create_or_get_user


def test_valid_and_invalid_state_transitions(
    client: TestClient, employee_headers: dict, reviewer_user, manager_user, db_session: Session, test_org: Organization
):
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

    # 5. Invalid Transition: Approved -> Archived (Approved decisions cannot be archived)
    res = client.patch(
        f"/decisions/{dec_id}/status",
        json={"status": "Archived"},
        headers=employee_headers,
    )
    assert res.status_code == 400
    assert "cannot be archived" in res.json()["detail"].lower() or "invalid state transition" in res.json()["detail"].lower()

    # 6. Approved decisions cannot be deleted
    res = client.delete(
        f"/decisions/{dec_id}",
        headers=employee_headers,
    )
    assert res.status_code == 400
    assert "cannot be deleted" in res.json()["detail"].lower()

    # 7. Create a second decision to test Draft -> Archived and Archived immutability
    res_arch = client.post(
        "/decisions",
        json={
            "title": f"Archived Test Decision {unique_id}",
            "problem_statement": "Testing archival from draft state.",
            "category": "Architecture",
        },
        headers=employee_headers,
    )
    assert res_arch.status_code == 201
    arch_id = res_arch.json()["id"]

    res = client.patch(
        f"/decisions/{arch_id}/status",
        json={"status": "Archived"},
        headers=employee_headers,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "Archived"

    # 8. Invalid Transition: Archived -> Draft
    res = client.patch(
        f"/decisions/{arch_id}/status",
        json={"status": "Draft"},
        headers=employee_headers,
    )
    assert res.status_code == 400
    assert "Cannot modify an archived decision" in res.json()["detail"] or "Invalid state transition" in res.json()["detail"]

    # 9. Immutability of Archived Decision
    res = client.put(
        f"/decisions/{arch_id}",
        json={
            "title": "Attempted Edit On Archived",
            "problem_statement": "Should be rejected.",
            "category": "Architecture",
        },
        headers=employee_headers,
    )
    assert res.status_code == 400
    assert "Cannot modify an archived decision" in res.json()["detail"]

    # 10. Approved decision cannot be assigned to anyone
    res_assign_appr = client.post(
        "/approvals",
        json={"decision_id": dec_id, "reviewer_id": reviewer_user.id},
        headers=employee_headers,
    )
    assert res_assign_appr.status_code == 400
    assert "cannot assign reviewer to an approved decision" in res_assign_appr.json()["detail"].lower()

    # 11. After assigning to one person it cannot be assigned to any other
    res_dec3 = client.post(
        "/decisions",
        json={
            "title": f"Single Reviewer Test {unique_id}",
            "problem_statement": "Verifying single reviewer assignment rule.",
            "category": "Architecture",
        },
        headers=employee_headers,
    )
    assert res_dec3.status_code == 201
    dec3_id = res_dec3.json()["id"]

    # First assignment succeeds
    res_first = client.post(
        "/approvals",
        json={"decision_id": dec3_id, "reviewer_id": reviewer_user.id},
        headers=employee_headers,
    )
    assert res_first.status_code == 201

    # Second assignment to another person of the same reviewer tier fails
    reviewer_2 = create_or_get_user(
        db_session, f"rev2_{unique_id}@test.com", "Reviewer Two", UserRole.REVIEWER, test_org.id, "QA"
    )
    res_second = client.post(
        "/approvals",
        json={"decision_id": dec3_id, "reviewer_id": reviewer_2.id},
        headers=employee_headers,
    )
    assert res_second.status_code == 400
    assert "already assigned to this decision" in res_second.json()["detail"].lower()
