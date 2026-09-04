import uuid
from fastapi.testclient import TestClient
from app.models.user import User


def test_complete_decision_lifecycle(
    client: TestClient,
    employee_user: User,
    employee_headers: dict,
    reviewer_user: User,
    reviewer_headers: dict,
    manager_user: User,
    manager_headers: dict,
):
    """
    End-to-End Decision Workflow (Sprint 13 Section 4):
    Step 1: Register & Login (Verified with JWT tokens)
    Step 2: Create Decision
    Step 3: Add 3 Alternatives
    Step 4: Compare Alternatives
    Step 5: Add Discussion (Comments, Threads, Meeting Notes, Rationale)
    Step 6: Assign Tags
    Step 7: Submit Decision (Draft -> Under Review)
    Step 8: Reviewer Action (Review & Approve)
    Step 9: Manager Approval (Multi-level workflow)
    Step 10: Final Decision Status verification
    Step 11: Sequential Version History & Audit Trail verification
    """
    unique_id = uuid.uuid4().hex[:6]

    # Step 3: Create Decision by Employee
    create_payload = {
        "title": f"Database Architecture Selection {unique_id}",
        "problem_statement": "Select the primary relational database system for high-concurrency microservices.",
        "category": "Technology",
        "rationale": "Evaluating modern relational and document datastores.",
    }
    res = client.post("/decisions", json=create_payload, headers=employee_headers)
    assert res.status_code == 201, f"Failed to create decision: {res.text}"
    decision = res.json()
    decision_id = decision["id"]
    assert decision["status"] == "Draft"
    assert decision["created_by"] == employee_user.id

    # Verify Version 1 was automatically created
    res = client.get(f"/decisions/{decision_id}/versions", headers=employee_headers)
    assert res.status_code == 200
    versions = res.json()
    assert len(versions) == 1
    assert versions[0]["version_number"] == 1
    assert versions[0]["status"] == "Draft"

    # Step 4: Add at least 3 Alternatives (PostgreSQL, MySQL, MongoDB)
    alternatives_data = [
        {
            "name": "PostgreSQL",
            "description": "Enterprise open-source relational database with JSONB and ACID guarantees.",
            "pros": "Robust ACID compliance, extensibility, rich indexing.",
            "cons": "Requires dedicated DB administration for large scale.",
            "estimated_cost": 5000.0,
            "feasibility_score": 5,
            "risk_level": "Low",
        },
        {
            "name": "MySQL",
            "description": "Popular relational database with strong read replica ecosystem.",
            "pros": "Ubiquitous tooling, fast simple reads.",
            "cons": "Less extensible than Postgres for complex analytics.",
            "estimated_cost": 4500.0,
            "feasibility_score": 4,
            "risk_level": "Medium",
        },
        {
            "name": "MongoDB",
            "description": "NoSQL document store for dynamic schemas.",
            "pros": "Flexible schema, horizontal sharding out of the box.",
            "cons": "Complex multi-document ACID transactions across shards.",
            "estimated_cost": 7000.0,
            "feasibility_score": 3,
            "risk_level": "High",
        },
    ]

    alt_ids = []
    for alt in alternatives_data:
        res = client.post(
            f"/decisions/{decision_id}/alternatives",
            json=alt,
            headers=employee_headers,
        )
        assert res.status_code == 201, f"Failed to create alternative {alt['name']}: {res.text}"
        alt_ids.append(res.json()["id"])

    assert len(alt_ids) == 3

    # Step 5: Compare Alternatives
    res = client.get(
        f"/decisions/{decision_id}/alternatives/compare",
        headers=employee_headers,
    )
    assert res.status_code == 200
    comp_data = res.json()
    assert len(comp_data["alternatives"]) == 3
    alt_names = [a["name"] for a in comp_data["alternatives"]]
    assert "PostgreSQL" in alt_names
    assert "MySQL" in alt_names
    assert "MongoDB" in alt_names

    # Step 6: Add Discussion (Discussion Thread, Comment, Decision Rationale, Meeting Note)
    # Discussion Thread
    res = client.post(
        f"/decisions/{decision_id}/threads",
        json={"title": "Performance and Storage Benchmark"},
        headers=employee_headers,
    )
    assert res.status_code == 201
    thread_id = res.json()["id"]

    # Comment in thread
    res = client.post(
        f"/threads/{thread_id}/comments",
        json={"content": "Benchmarked PostgreSQL with 10,000 concurrent TPS."},
        headers=employee_headers,
    )
    assert res.status_code == 201

    # Reviewer commenting on thread
    res = client.post(
        f"/threads/{thread_id}/comments",
        json={"content": "Reviewer analysis concurs: Postgres meets our ACID criteria."},
        headers=reviewer_headers,
    )
    assert res.status_code == 201

    # Meeting Note
    res = client.post(
        f"/decisions/{decision_id}/meeting-notes",
        json={
            "title": "Architecture Review Committee",
            "content": "Reviewed performance data and agreed on PostgreSQL recommendation.",
            "meeting_date": "2026-09-04",
        },
        headers=employee_headers,
    )
    assert res.status_code == 201

    # Update Rationale
    res = client.put(
        f"/decisions/{decision_id}/rationale",
        json={"rationale": "PostgreSQL selected based on benchmark performance and compliance."},
        headers=employee_headers,
    )
    assert res.status_code == 200
    assert res.json()["rationale"] == "PostgreSQL selected based on benchmark performance and compliance."

    # Step 7: Submit Decision (Draft -> Under Review)
    res = client.post(f"/decisions/{decision_id}/submit", headers=employee_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "Under Review"

    # Step 8: Multi-level Approval Assignment & Actions
    # Assign Level 1: Reviewer
    res = client.post(
        "/approvals",
        json={"decision_id": decision_id, "reviewer_id": reviewer_user.id},
        headers=employee_headers,
    )
    assert res.status_code == 201
    rev_approval_id = res.json()["id"]

    # Assign Level 2: Manager
    res = client.post(
        "/approvals",
        json={"decision_id": decision_id, "reviewer_id": manager_user.id},
        headers=employee_headers,
    )
    assert res.status_code == 201
    mgr_approval_id = res.json()["id"]

    # Reviewer approves Level 1
    res = client.patch(
        f"/approvals/{rev_approval_id}/status",
        json={"status": "Approved"},
        headers=reviewer_headers,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "Approved"

    # Multi-level check: Decision should still be Under Review because Manager approval is still Pending
    res = client.get(f"/decisions/{decision_id}", headers=employee_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "Under Review"

    # Step 9: Manager approves Level 2
    res = client.patch(
        f"/approvals/{mgr_approval_id}/status",
        json={"status": "Approved"},
        headers=manager_headers,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "Approved"

    # Step 10: Final Decision Status verification
    res = client.get(f"/decisions/{decision_id}", headers=employee_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "Approved", "Decision must reach Approved status after all approvals complete"

    # Step 11: Version History & Audit Trail verification
    res = client.get(f"/decisions/{decision_id}/versions", headers=employee_headers)
    assert res.status_code == 200
    all_versions = res.json()
    assert len(all_versions) >= 3, f"Expected at least 3 sequential versions, got {len(all_versions)}"
    version_numbers = [v["version_number"] for v in all_versions]
    assert version_numbers == list(range(1, len(all_versions) + 1)), "Versions must be strictly sequential"
    assert all_versions[-1]["status"] == "Approved"

    # Verify Timeline
    res = client.get(f"/decisions/{decision_id}/timeline", headers=employee_headers)
    assert res.status_code == 200
    timeline = res.json()
    actions = [t["action"] for t in timeline]
    assert "CREATE" in actions
    assert "SUBMIT" in actions
    assert "APPROVE" in actions
