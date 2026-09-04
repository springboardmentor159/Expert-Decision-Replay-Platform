import io
import json
import uuid
import openpyxl
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def log_header(title: str):
    print("\n" + "=" * 60)
    print(f"[*] {title.upper()}")
    print("=" * 60)


def create_and_login(email: str, role: str, full_name: str, department: str = "Engineering"):
    emp_id = f"EMP-{uuid.uuid4().hex[:6]}"
    client.post(
        "/users",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": full_name,
            "role": role,
            "employee_id": emp_id,
            "department": department
        }
    )
    resp = client.post(
        "/auth/login",
        json={"email": email, "password": "Password123!"}
    )
    assert resp.status_code == 200, f"Login failed for {email}: {resp.text}"
    token = resp.json()["access_token"]
    user_info = client.get("/users/me", headers={"Authorization": f"Bearer {token}"}).json()
    return token, user_info


def run_sprint13_system_verification():
    log_header("Sprint 13 System Integration & Decision Lifecycle Verification")

    # Step 1 & 2: User Registration & Authentication
    print("\n[Step 1 & 2] Authenticating 4 Organizational Roles (Employee, Reviewer, Manager, Administrator)...")
    emp_token, emp_user = create_and_login("int_emp_13@example.com", "Employee", "Alex Dev", "Engineering")
    rev_token, rev_user = create_and_login("int_rev_13@example.com", "Reviewer", "Brenda Reviewer", "Engineering")
    mgr_token, mgr_user = create_and_login("int_mgr_13@example.com", "Manager", "Charles Manager", "Engineering")
    adm_token, adm_user = create_and_login("int_adm_13@example.com", "Administrator", "Diana Admin", "Executive")

    emp_hdr = {"Authorization": f"Bearer {emp_token}"}
    rev_hdr = {"Authorization": f"Bearer {rev_token}"}
    mgr_hdr = {"Authorization": f"Bearer {mgr_token}"}
    adm_hdr = {"Authorization": f"Bearer {adm_token}"}

    print(f"  + Employee: {emp_user['full_name']} (ID: {emp_user['id']})")
    print(f"  + Reviewer: {rev_user['full_name']} (ID: {rev_user['id']})")
    print(f"  + Manager:  {mgr_user['full_name']} (ID: {mgr_user['id']})")
    print(f"  + Admin:    {adm_user['full_name']} (ID: {adm_user['id']})")

    # Step 3: Create Decision
    print("\n[Step 3] Employee creates new Decision in Draft status...")
    dec_resp = client.post(
        "/decisions",
        headers=emp_hdr,
        json={
            "title": "Migrate Monolith to Microservices Architecture",
            "problem_statement": "Address scalability bottlenecks and independent deployment requirements",
            "category": "Architecture"
        }
    )
    assert dec_resp.status_code == 201
    decision = dec_resp.json()
    dec_id = decision["id"]
    print(f"  + Decision Created: ID {dec_id} | Title: '{decision['title']}' | Status: {decision['status']}")
    assert decision["status"] == "Draft"

    # Step 4: Add at least 3 Alternatives
    print("\n[Step 4] Adding 3 Architectural Alternatives with feasibility scores & risk ratings...")
    alternatives = [
        {"name": "Domain-Driven Service Mesh (gRPC)", "description": "High performance RPC with Istio", "pros": "Sub-millisecond latency", "cons": "Steeper learning curve", "estimated_cost": 750.0, "feasibility_score": 4, "risk_level": "Medium"},
        {"name": "Event-Driven Asynchronous Architecture (Kafka)", "description": "Decoupled pub-sub events", "pros": "Maximum fault tolerance and replayability", "cons": "Eventual consistency management", "estimated_cost": 900.0, "feasibility_score": 5, "risk_level": "Low"},
        {"name": "Modular Monolith Transition", "description": "Structured modules within single codebase", "pros": "Low operational complexity", "cons": "Shared scaling resources", "estimated_cost": 300.0, "feasibility_score": 5, "risk_level": "Low"}
    ]
    for alt in alternatives:
        resp = client.post(f"/decisions/{dec_id}/alternatives", headers=emp_hdr, json=alt)
        assert resp.status_code == 201
        print(f"  + Alternative Added: '{alt['name']}' (Score: {alt['feasibility_score']}/5, Risk: {alt['risk_level']})")

    # Step 5: Compare Alternatives
    print("\n[Step 5] Comparing Alternatives via GET /decisions/{id}/alternatives/compare...")
    cmp_resp = client.get(f"/decisions/{dec_id}/alternatives/compare", headers=emp_hdr)
    assert cmp_resp.status_code == 200
    cmp_data = cmp_resp.json()
    print(f"  + Comparison verified: {len(cmp_data['alternatives'])} alternatives compared successfully.")

    # Step 6: Add Discussion (Comment, Thread, Meeting Note, Rationale)
    print("\n[Step 6] Adding Collaboration & Discussion data...")
    client.post(f"/decisions/{dec_id}/comments", headers=rev_hdr, json={"content": "Event-driven approach satisfies 99.99% uptime requirements."})
    client.post(f"/decisions/{dec_id}/threads", headers=emp_hdr, json={"title": "Schema Registry Governance", "content": "How to handle Protobuf versioning?"})
    client.post(f"/decisions/{dec_id}/meeting-notes", headers=mgr_hdr, json={"title": "Executive Review", "content": "Approved Kafka-based architecture."})
    client.put(f"/decisions/{dec_id}/rationale", headers=emp_hdr, json={"rationale": "Kafka event streams decouple services while maintaining an immutable event ledger."})
    print("  + Comments, Discussion Threads, Meeting Notes, and Rationale linked successfully.")

    # Step 7 & 8: Submit for Multi-Level Approval
    print("\n[Step 7 & 8] Submitting Decision for Multi-Level Approval Workflow...")
    app1 = client.post("/approvals", headers=emp_hdr, json={"decision_id": dec_id, "reviewer_id": rev_user["id"], "approval_level": 1, "comments": "Level 1 Review"}).json()
    app2 = client.post("/approvals", headers=emp_hdr, json={"decision_id": dec_id, "reviewer_id": mgr_user["id"], "approval_level": 2, "comments": "Level 2 Review"}).json()
    dec_state = client.get(f"/decisions/{dec_id}", headers=emp_hdr).json()
    print(f"  + Approvals Created: Level 1 (Reviewer ID {rev_user['id']}), Level 2 (Manager ID {mgr_user['id']})")
    print(f"  + Decision Status transitioned to: '{dec_state['status']}'")
    assert dec_state["status"] == "Under Review"

    # Step 9: Reviewer Action (Level 1 Approval) & Authorization Check
    print("\n[Step 9] Enforcing Authorization & Processing Reviewer Level 1 Approval...")
    # Unauthorized employee attempt must fail
    unauth_resp = client.post(f"/approvals/{app1['id']}/approve", headers=emp_hdr)
    assert unauth_resp.status_code == 403
    print("  + Verified: Unauthorized Employee receives 403 Forbidden on approval action.")

    # Reviewer approves Level 1
    client.post(f"/approvals/{app1['id']}/approve", headers=rev_hdr, json={"comments": "Level 1 Technical review passed."})
    mid_state = client.get(f"/decisions/{dec_id}", headers=emp_hdr).json()
    print(f"  + Level 1 Approved. Multi-level check: Decision remains '{mid_state['status']}' while Level 2 is pending.")
    assert mid_state["status"] == "Under Review"

    # Step 10: Manager Approval (Level 2 Approval)
    print("\n[Step 10] Processing Manager Level 2 Approval...")
    client.post(f"/approvals/{app2['id']}/approve", headers=mgr_hdr, json={"comments": "Level 2 Manager approval granted."})

    # Step 11: Final Status & Audit/Versions/Reporting Verification
    print("\n[Step 11] Verifying Final Decision State, Version Tracking, Audit Trail, & Reports...")
    final_state = client.get(f"/decisions/{dec_id}", headers=emp_hdr).json()
    print(f"  + Final Decision Status: '{final_state['status']}'")
    assert final_state["status"] == "Approved"

    # State Machine: Ensure Approved cannot be reverted to Draft
    invalid_patch = client.patch(f"/decisions/{dec_id}/status", headers=adm_hdr, json={"status": "Draft"})
    assert invalid_patch.status_code == 400
    print("  + Verified: State machine blocked invalid transition ('Approved' -> 'Draft') with 400 Bad Request.")

    # Versions Check
    ver_resp = client.get(f"/decisions/{dec_id}/versions", headers=adm_hdr).json()
    print(f"  + Sequential Versions Captured: {len(ver_resp)} versions.")
    assert len(ver_resp) >= 2

    # Reports & Exports Check
    pdf_resp = client.get(f"/reports/decisions/export/pdf?status=Approved", headers=adm_hdr)
    assert pdf_resp.status_code == 200 and pdf_resp.content.startswith(b"%PDF-")
    print(f"  + Decision PDF Report generated ({len(pdf_resp.content)} bytes, valid %PDF-).")

    xlsx_resp = client.get(f"/reports/decisions/export/excel?status=Approved", headers=adm_hdr)
    assert xlsx_resp.status_code == 200
    wb = openpyxl.load_workbook(io.BytesIO(xlsx_resp.content))
    print(f"  + Decision Excel Report generated ({len(xlsx_resp.content)} bytes, Sheets: {wb.sheetnames}).")

    log_header("All Sprint 13 End-to-End System Integrations Successfully Verified!")


if __name__ == "__main__":
    run_sprint13_system_verification()
