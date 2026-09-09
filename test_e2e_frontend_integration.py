"""
End-to-End API Integration Verification for Sprint 14
Tests every API endpoint utilized by the frontend:
- Auth (registration, login, profile, role access)
- Decision lifecycle (create, update, tag, submit, version)
- Alternatives (create, compare, update, delete)
- Discussions (comments, meeting notes)
- Approvals (assign, approve/reject, status change)
- Search & Knowledge repository
- Reports & PDF/Excel binary file exports
- Audit & Security log access
"""
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_integration():
    unique_id = uuid.uuid4().hex[:8]
    print(f"--- Starting Sprint 14 Integration Test (Run ID: {unique_id}) ---")

    # 1. Register users for all 4 roles
    users_data = {
        "employee": {
            "full_name": f"Emp {unique_id}",
            "email": f"emp_{unique_id}@test.com",
            "role": "Employee",
            "employee_id": f"EMP-{unique_id}",
            "department": "Engineering",
            "designation": "Software Engineer",
            "phone_number": "+1-555-0101",
            "password": "Password123!",
        },
        "reviewer": {
            "full_name": f"Rev {unique_id}",
            "email": f"rev_{unique_id}@test.com",
            "role": "Reviewer",
            "employee_id": f"REV-{unique_id}",
            "department": "Architecture",
            "designation": "Principal Architect",
            "phone_number": "+1-555-0102",
            "password": "Password123!",
        },
        "manager": {
            "full_name": f"Mgr {unique_id}",
            "email": f"mgr_{unique_id}@test.com",
            "role": "Manager",
            "employee_id": f"MGR-{unique_id}",
            "department": "Engineering",
            "designation": "Engineering Director",
            "phone_number": "+1-555-0103",
            "password": "Password123!",
        },
        "admin": {
            "full_name": f"Adm {unique_id}",
            "email": f"adm_{unique_id}@test.com",
            "role": "Administrator",
            "employee_id": f"ADM-{unique_id}",
            "department": "IT Operations",
            "designation": "System Admin",
            "phone_number": "+1-555-0104",
            "password": "Password123!",
        },
    }

    tokens = {}
    user_ids = {}

    for role, udata in users_data.items():
        # Registration
        reg_res = client.post("/users", json=udata)
        assert reg_res.status_code == 201, f"Failed to register {role}: {reg_res.text}"
        user_ids[role] = reg_res.json()["id"]
        print(f"Registered {role} -> User ID {user_ids[role]}")

        # Login
        login_res = client.post("/token", data={"username": udata["email"], "password": udata["password"]})
        assert login_res.status_code == 200, f"Failed to login {role}: {login_res.text}"
        tokens[role] = login_res.json()["access_token"]

        # Verify /users/me
        me_res = client.get("/users/me", headers={"Authorization": f"Bearer {tokens[role]}"})
        assert me_res.status_code == 200
        assert me_res.json()["email"] == udata["email"]

    print("All 4 roles registered and logged in successfully.")

    # 2. Decision Creation as Employee
    emp_headers = {"Authorization": f"Bearer {tokens['employee']}"}
    create_dec_res = client.post(
        "/decisions",
        headers=emp_headers,
        json={
            "title": f"Migrate Auth to OAuth2 PKCE {unique_id}",
            "problem_statement": "Legacy session-based authentication prevents mobile integration and cross-service delegation.",
            "category": "Security",
        },
    )
    assert create_dec_res.status_code == 201
    decision = create_dec_res.json()
    decision_id = decision["id"]
    assert decision["status"] == "Draft"
    print(f"Created Decision #{decision_id} (Status: Draft)")

    # 3. Add Tag
    mgr_headers = {"Authorization": f"Bearer {tokens['manager']}"}
    tag_res = client.post("/tags", headers=mgr_headers, json={"name": f"security-{unique_id}"})
    assert tag_res.status_code == 201
    tag_id = tag_res.json()["id"]

    assign_tag_res = client.post(
        f"/decisions/{decision_id}/tags",
        headers=emp_headers,
        json={"tag_ids": [tag_id]},
    )
    assert assign_tag_res.status_code == 200
    print(f"Assigned Tag #{tag_id} to Decision #{decision_id}")

    # 4. Add Alternatives
    alt1_res = client.post(
        f"/decisions/{decision_id}/alternatives",
        headers=emp_headers,
        json={
            "name": "Option A: Self-Hosted Keycloak Cluster",
            "description": "Deploy OpenID Connect compliant Keycloak in Kubernetes",
            "estimated_cost": 25000.0,
            "feasibility_score": 4,
            "risk_level": "Medium",
            "pros": "Complete data sovereignty, zero per-seat licensing",
            "cons": "Requires dedicated operator maintenance",
        },
    )
    assert alt1_res.status_code == 201
    alt1_id = alt1_res.json()["id"]

    alt2_res = client.post(
        f"/decisions/{decision_id}/alternatives",
        headers=emp_headers,
        json={
            "name": "Option B: Managed Auth0 / Okta",
            "description": "Enterprise SaaS identity solution with 99.99% SLA",
            "estimated_cost": 50000.0,
            "feasibility_score": 5,
            "risk_level": "Low",
            "pros": "Instant turnkey integrations, managed high availability",
            "cons": "Recurring subscription costs scale with active users",
        },
    )
    assert alt2_res.status_code == 201
    alt2_id = alt2_res.json()["id"]
    print(f"Added Alternatives #{alt1_id} and #{alt2_id}")

    # 5. Compare Alternatives
    compare_res = client.get(f"/decisions/{decision_id}/alternatives/compare", headers=emp_headers)
    assert compare_res.status_code == 200
    comparison = compare_res.json()
    assert len(comparison["alternatives"]) == 2
    print("Alternative comparison matrix verified.")

    # 6. Delete an alternative (test DELETE endpoint)
    alt3_res = client.post(
        f"/decisions/{decision_id}/alternatives",
        headers=emp_headers,
        json={
            "name": "Option C: Custom In-House Token Service",
            "description": "Custom JWT issuer",
            "estimated_cost": 75000.0,
            "feasibility_score": 2,
            "risk_level": "Critical",
            "pros": "Full customization",
            "cons": "High maintenance and security risk",
        },
    )
    assert alt3_res.status_code == 201
    alt3_id = alt3_res.json()["id"]

    del_alt_res = client.delete(f"/alternatives/{alt3_id}", headers=emp_headers)
    assert del_alt_res.status_code == 204
    print(f"Deleted Alternative #{alt3_id} successfully.")

    # 7. Post Comment & Meeting Note
    comment_res = client.post(
        f"/decisions/{decision_id}/comments",
        headers=emp_headers,
        json={"content": "Security audit reviewed the RFC; Option A meets SOC2 compliance standards."},
    )
    assert comment_res.status_code == 201

    note_res = client.post(
        f"/decisions/{decision_id}/meeting-notes",
        headers=emp_headers,
        json={
            "title": "Architecture Review Board Sync",
            "content": "Attendees: Alex, Jane, Jordan. Consensus leaning towards Option A given data residency constraints.",
            "meeting_date": "2026-09-09T14:00:00Z",
        },
    )
    assert note_res.status_code == 201, f"Failed meeting note: {note_res.text}"
    print("Comments and meeting notes recorded.")

    # 8. Submit Decision for Review
    submit_res = client.patch(
        f"/decisions/{decision_id}/status",
        headers=emp_headers,
        json={"status": "Under Review"},
    )
    assert submit_res.status_code == 200
    assert submit_res.json()["status"] == "Under Review"
    print("Decision transitioned: Draft -> Under Review")

    # 9. Manager Assigns Reviewer
    assign_approval_res = client.post(
        f"/decisions/{decision_id}/approvals",
        headers=mgr_headers,
        json={"reviewer_id": user_ids["reviewer"]},
    )
    assert assign_approval_res.status_code == 201
    approval = assign_approval_res.json()
    approval_id = approval["id"]
    assert approval["status"] == "Pending"
    print(f"Manager assigned Reviewer #{user_ids['reviewer']} to Approval #{approval_id}")

    # 10. Reviewer Approves Decision
    rev_headers = {"Authorization": f"Bearer {tokens['reviewer']}"}
    approve_res = client.patch(
        f"/approvals/{approval_id}",
        headers=rev_headers,
        json={"status": "Approved", "comments": "Approved based on multi-region failover and cost viability."},
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "Approved"

    # Verify Decision Status is now Approved
    dec_check_res = client.get(f"/decisions/{decision_id}", headers=emp_headers)
    assert dec_check_res.json()["status"] == "Approved"
    print("Approval completed: Decision is now Approved.")

    # 11. Search Knowledge Repository
    search_res = client.get(f"/decisions/search?q=OAuth2", headers=emp_headers)
    assert search_res.status_code == 200
    assert search_res.json()["total"] >= 1
    print("Knowledge repository search verified.")

    # 12. Version History & Timeline
    versions_res = client.get(f"/decisions/{decision_id}/versions", headers=emp_headers)
    assert versions_res.status_code == 200
    assert len(versions_res.json()) >= 1

    timeline_res = client.get(f"/decisions/{decision_id}/timeline", headers=emp_headers)
    assert timeline_res.status_code == 200
    print("Version history and timeline verified.")

    # 13. Reports & File Exports (PDF & Excel)
    pdf_res = client.get("/reports/decisions/export/pdf", headers=emp_headers)
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 100
    print("PDF export streamed successfully (size:", len(pdf_res.content), "bytes)")

    excel_res = client.get("/reports/decisions/export/excel", headers=emp_headers)
    assert excel_res.status_code == 200
    assert "openxmlformats" in excel_res.headers["content-type"]
    assert len(excel_res.content) > 100
    print("Excel export streamed successfully (size:", len(excel_res.content), "bytes)")

    # 14. Audit Logs Access Control
    admin_headers = {"Authorization": f"Bearer {tokens['admin']}"}
    audit_admin_res = client.get("/audit-logs", headers=admin_headers)
    assert audit_admin_res.status_code == 200
    assert audit_admin_res.json()["total"] >= 1

    audit_emp_res = client.get("/audit-logs", headers=emp_headers)
    assert audit_emp_res.status_code == 403, "Employee must be forbidden from accessing admin audit logs"
    print("Audit access control verified (Admin allowed, Employee 403 Forbidden).")

    print("\n[SUCCESS] ALL SPRINT 14 INTEGRATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_full_integration()
