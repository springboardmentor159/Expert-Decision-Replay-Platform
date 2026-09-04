import time
import uuid
from fastapi.testclient import TestClient
from app.models.user import User


def test_concurrency_conflict_handling(
    client: TestClient,
    employee_headers: dict,
    reviewer_user: User,
    reviewer_headers: dict,
):
    """
    Test Concurrency & Duplicate Action Protection (Sprint 13 Section 27):
    - Re-approving already completed approval returns 409 Conflict.
    - Assigning duplicate pending approval to same reviewer returns 409 Conflict.
    """
    unique_id = uuid.uuid4().hex[:6]

    # Create Decision
    res = client.post(
        "/decisions",
        json={
            "title": f"Concurrency Test Decision {unique_id}",
            "problem_statement": "Testing concurrent operations.",
            "category": "Technology",
        },
        headers=employee_headers,
    )
    assert res.status_code == 201
    dec_id = res.json()["id"]

    # Submit
    client.post(f"/decisions/{dec_id}/submit", headers=employee_headers)

    # Assign Approval
    res = client.post(
        "/approvals",
        json={"decision_id": dec_id, "reviewer_id": reviewer_user.id},
        headers=employee_headers,
    )
    assert res.status_code == 201
    appr_id = res.json()["id"]

    # Assign DUPLICATE pending approval -> Expected 409 Conflict
    res_dup = client.post(
        "/approvals",
        json={"decision_id": dec_id, "reviewer_id": reviewer_user.id},
        headers=employee_headers,
    )
    assert res_dup.status_code == 409, f"Expected 409 Conflict for duplicate approval, got {res_dup.status_code}"

    # Reviewer approves
    res_appr1 = client.patch(
        f"/approvals/{appr_id}/status",
        json={"status": "Approved"},
        headers=reviewer_headers,
    )
    assert res_appr1.status_code == 200

    # Reviewer attempts SECOND approval on already completed approval -> Expected 409 Conflict
    res_appr2 = client.patch(
        f"/approvals/{appr_id}/status",
        json={"status": "Approved"},
        headers=reviewer_headers,
    )
    assert res_appr2.status_code == 409, f"Expected 409 Conflict when completing already approved approval, got {res_appr2.status_code}"


def test_endpoint_performance_baselines(
    client: TestClient,
    employee_headers: dict,
    admin_headers: dict,
):
    """
    Basic Performance Testing (Sprint 13 Section 26):
    Ensure core API responses complete within reasonable performance thresholds.
    """
    # 1. Decision Search Latency
    start = time.perf_counter()
    res = client.get("/decisions/search?q=Architecture", headers=employee_headers)
    search_duration = time.perf_counter() - start
    assert res.status_code == 200
    assert search_duration < 1.0, f"Decision search took {search_duration:.2f}s, expected < 1.0s"

    # 2. Dashboard Analytics Latency
    start = time.perf_counter()
    res = client.get("/dashboard/admin/analytics", headers=admin_headers)
    dash_duration = time.perf_counter() - start
    assert res.status_code == 200
    assert dash_duration < 1.0, f"Dashboard analytics took {dash_duration:.2f}s, expected < 1.0s"

    # 3. Decision Report Generation Latency
    start = time.perf_counter()
    res = client.get("/reports/decisions?page=1&page_size=20", headers=admin_headers)
    report_duration = time.perf_counter() - start
    assert res.status_code == 200
    assert report_duration < 1.5, f"Report generation took {report_duration:.2f}s, expected < 1.5s"
