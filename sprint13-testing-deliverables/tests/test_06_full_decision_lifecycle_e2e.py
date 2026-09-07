"""
Sprint 13 - Sections 4, 21 & 34: End-to-End Decision Workflow /
API Integration Testing / Final Integration Test.

One continuous, ordered scenario that walks the complete decision
lifecycle exactly as the sprint doc lays it out:

  Register -> Login -> Create Decision -> Add Alternatives ->
  Compare Alternatives -> Add Discussion (thread, comment, meeting
  note, rationale) -> Submit for Review -> Reviewer Action ->
  Decision Outcome -> Audit History -> Version History -> Dashboard ->
  Reports (PDF/Excel)

Each step asserts on the *previous* step's output, so a break anywhere
in the chain fails fast at the point of the break rather than surfacing
as an unrelated failure later in the suite.
"""
import uuid


def test_full_decision_lifecycle_workflow(
    api, employee_user, manager_user, reviewer_user, admin_user
):
    headers_employee = employee_user["headers"]
    headers_manager = manager_user["headers"]
    headers_reviewer = reviewer_user["headers"]
    headers_admin = admin_user["headers"]

    # ---- Step 1-2: users already registered & logged in via fixtures ----
    assert employee_user["token"]
    assert manager_user["token"]
    assert reviewer_user["token"]
    assert admin_user["token"]

    # ---- Step 3: Create Decision (Employee) ----
    title = f"Primary datastore selection {uuid.uuid4().hex[:6]}"
    create_resp = api.post(
        "/decisions",
        json={
            "title": title,
            "problem_statement": "We need to pick a primary datastore for the new service.",
            "category": "Technology",
        },
        headers=headers_employee,
    )
    assert create_resp.status_code == 201, create_resp.text
    decision = create_resp.json()
    decision_id = decision["id"]
    assert decision["title"] == title
    assert decision["status"] == "Draft"
    assert decision["created_by"] == employee_user["id"]

    # ---- Step 4: Add at least 3 alternatives ----
    alt_specs = [
        ("PostgreSQL", 4, "Low", 5000),
        ("MySQL", 4, "Low", 4500),
        ("MongoDB", 3, "Medium", 6000),
    ]
    created_alt_ids = []
    for name, score, risk, cost in alt_specs:
        resp = api.post(
            f"/decisions/{decision_id}/alternatives",
            json={
                "name": name,
                "description": f"{name} as a candidate datastore",
                "pros": "Well understood by the team",
                "cons": "Operational overhead",
                "estimated_cost": cost,
                "feasibility_score": score,
                "risk_level": risk,
            },
            headers=headers_employee,
        )
        assert resp.status_code == 201, resp.text
        alt = resp.json()
        assert alt["decision_id"] == decision_id
        assert 1 <= alt["feasibility_score"] <= 5
        assert alt["risk_level"] in ("Low", "Medium", "High", "Critical")
        created_alt_ids.append(alt["id"])

    list_resp = api.get(f"/decisions/{decision_id}/alternatives", headers=headers_employee)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 3
    assert {a["id"] for a in list_resp.json()} == set(created_alt_ids)

    # ---- Step 5: Compare alternatives ----
    compare_resp = api.get(
        f"/decisions/{decision_id}/alternatives/compare", headers=headers_employee
    )
    assert compare_resp.status_code == 200, compare_resp.text
    compare_body = compare_resp.json()
    assert compare_body["decision_id"] == decision_id
    assert len(compare_body["alternatives"]) == 3

    # ---- Step 6: Add discussion (thread, comment, rationale, meeting note) ----
    thread_resp = api.post(
        f"/decisions/{decision_id}/threads",
        json={"title": "Which datastore should we pick?", "description": "Kickoff discussion"},
        headers=headers_employee,
    )
    assert thread_resp.status_code == 201, thread_resp.text
    thread = thread_resp.json()
    assert thread["decision_id"] == decision_id
    assert thread["created_by"] == employee_user["id"]

    comment_resp = api.post(
        f"/decisions/{decision_id}/comments",
        json={"content": "I'd lean towards PostgreSQL for ACID guarantees."},
        headers=headers_manager,
    )
    assert comment_resp.status_code == 201, comment_resp.text
    comment = comment_resp.json()
    assert comment["decision_id"] == decision_id
    assert comment["user_id"] == manager_user["id"]

    rationale_resp = api.put(
        f"/decisions/{decision_id}/rationale",
        json={"rationale": "PostgreSQL best balances team familiarity and reliability."},
        headers=headers_employee,
    )
    assert rationale_resp.status_code == 200
    assert rationale_resp.json()["decision_id"] == decision_id

    note_resp = api.post(
        f"/decisions/{decision_id}/meeting-notes",
        json={
            "title": "Architecture review",
            "content": "Team agreed PostgreSQL is the frontrunner pending load testing.",
            "meeting_date": "2026-09-01T10:00:00",
        },
        headers=headers_employee,
    )
    assert note_resp.status_code == 201, note_resp.text

    # ---- Step 8: Submit decision: Draft -> Under Review ----
    submit_resp = api.patch(
        f"/decisions/{decision_id}/status",
        json={"status": "Under Review"},
        headers=headers_employee,
    )
    assert submit_resp.status_code == 200, submit_resp.text
    assert submit_resp.json()["status"] == "Under Review"

    # ---- Step 9: Reviewer assignment + action ----
    assign_resp = api.post(
        f"/decisions/{decision_id}/approvals",
        json={"level": 1, "reviewer_id": reviewer_user["id"]},
        headers=headers_manager,
    )
    assert assign_resp.status_code == 201, assign_resp.text
    approval = assign_resp.json()
    assert approval["status"] == "Pending"
    assert approval["reviewer_id"] == reviewer_user["id"]

    # Wrong reviewer cannot act on somebody else's assignment.
    forbidden_resp = api.patch(
        f"/approvals/{approval['id']}",
        json={"decision": "Approved"},
        headers=headers_employee,
    )
    assert forbidden_resp.status_code == 403

    approve_resp = api.patch(
        f"/approvals/{approval['id']}",
        json={"decision": "Approved", "comments": "Looks solid, approved."},
        headers=headers_reviewer,
    )
    assert approve_resp.status_code == 200, approve_resp.text
    assert approve_resp.json()["status"] == "Approved"

    # A completed approval cannot be actioned again.
    replay_resp = api.patch(
        f"/approvals/{approval['id']}",
        json={"decision": "Rejected"},
        headers=headers_reviewer,
    )
    assert replay_resp.status_code == 400

    # ---- Step 11: Final decision status ----
    final_resp = api.get(f"/decisions/{decision_id}", headers=headers_employee)
    assert final_resp.status_code == 200
    assert final_resp.json()["status"] == "Approved"

    # ---- Section 13/14: Audit trail + version history ----
    versions_resp = api.get(f"/decisions/{decision_id}/versions", headers=headers_employee)
    assert versions_resp.status_code == 200
    versions = versions_resp.json()
    assert len(versions) >= 3  # create, submit, approve at minimum
    version_numbers = [v["version_number"] for v in versions]
    assert version_numbers == sorted(version_numbers)

    one_version_resp = api.get(
        f"/decisions/{decision_id}/versions/{versions[0]['version_number']}",
        headers=headers_employee,
    )
    assert one_version_resp.status_code == 200

    history_resp = api.get(f"/decisions/{decision_id}/history", headers=headers_employee)
    assert history_resp.status_code == 200
    history_events = history_resp.json()["history"]
    assert len(history_events) > 0
    timestamps = [e["timestamp"] for e in history_events]
    assert timestamps == sorted(timestamps)

    audit_resp = api.get(
        "/audit-logs",
        params={"entity_type": "Decision", "entity_id": decision_id},
        headers=headers_admin,
    )
    assert audit_resp.status_code == 200
    audit_actions = {row["action"] for row in audit_resp.json()["items"]}
    assert "CREATE" in audit_actions

    # ---- Section 15: Dashboards reflect the new data ----
    emp_dash = api.get("/dashboard/employee", headers=headers_employee)
    assert emp_dash.status_code == 200

    admin_dash = api.get("/dashboard/admin", headers=headers_admin)
    assert admin_dash.status_code == 200

    # ---- Section 16: Search / filtering surfaces the decision ----
    search_resp = api.get(
        "/decisions/search",
        params={"q": title.split()[0], "status": "Approved"},
        headers=headers_employee,
    )
    assert search_resp.status_code == 200
    found_ids = {item["id"] for item in search_resp.json()["items"]}
    assert decision_id in found_ids

    # ---- Section 17/18/19: Reports + PDF/Excel export ----
    report_resp = api.get(
        "/reports/decisions",
        params={"status": "Approved"},
        headers=headers_manager,
    )
    assert report_resp.status_code == 200
    report_ids = {item["decision_id"] for item in report_resp.json()["items"]}
    assert decision_id in report_ids

    pdf_resp = api.get(
        "/reports/decisions/export/pdf",
        params={"status": "Approved"},
        headers=headers_manager,
    )
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers.get("content-type", "").startswith("application/pdf")
    assert pdf_resp.content[:4] == b"%PDF"

    excel_resp = api.get(
        "/reports/decisions/export/excel",
        params={"status": "Approved"},
        headers=headers_manager,
    )
    assert excel_resp.status_code == 200
    assert "spreadsheet" in excel_resp.headers.get("content-type", "") or excel_resp.content[:2] == b"PK"
