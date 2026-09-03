import io
import json
import uuid
import openpyxl
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def log_step(step: str, detail: str = ""):
    print(f"\n==================================================")
    print(f"[*] STEP: {step}")
    if detail:
        print(f"    {detail}")
    print(f"==================================================")


def get_token(email: str, role: str, full_name: str, department: str = "Engineering") -> str:
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
        json={
            "email": email,
            "password": "Password123!"
        }
    )
    if resp.status_code != 200:
        raise Exception(f"Login failed for {email}: {resp.text}")
    return resp.json()["access_token"]


def run_verification():
    print("\n--- STARTING SPRINT 12 CENTRALIZED REPORTING VERIFICATION ---")

    # 1. User Creation & Authentication
    log_step("1. Authenticate Users & Verify Roles", "Create Admin, Manager, and Employee")
    admin_token = get_token("admin_e2e@example.com", "Administrator", "Super Admin", "Executive")
    mgr_eng_token = get_token("mgr_e2e_eng@example.com", "Manager", "Eng Manager", "Engineering")
    emp_token = get_token("emp_e2e@example.com", "Employee", "John Developer", "Engineering")

    admin_hdr = {"Authorization": f"Bearer {admin_token}"}
    mgr_hdr = {"Authorization": f"Bearer {mgr_eng_token}"}
    emp_hdr = {"Authorization": f"Bearer {emp_token}"}

    # 2. Seed Data: Decisions, Alternatives, Approvals
    log_step("2. Populate Platform Data for Reporting", "Create Decisions, Alternatives, Approvals")
    d1 = client.post(
        "/decisions",
        headers=admin_hdr,
        json={"title": "Adopt PostgreSQL for Reporting DB", "problem_statement": "Fast queries & JSONB", "category": "Database Architecture"}
    ).json()
    d1_id = d1["id"]

    d2 = client.post(
        "/decisions",
        headers=mgr_hdr,
        json={"title": "Implement ReportLab for PDF", "problem_statement": "Automated PDF rendering", "category": "Reporting Engine"}
    ).json()
    d2_id = d2["id"]

    # Add alternative
    client.post(
        f"/decisions/{d1_id}/alternatives",
        headers=admin_hdr,
        json={"name": "PostgreSQL 16", "description": "Relational engine", "estimated_cost": 350.0, "feasibility_score": 5, "risk_level": "Low"}
    )

    # Add approval
    rev_token = get_token("rev_e2e@example.com", "Reviewer", "Jane Reviewer", "Engineering")
    rev_hdr = {"Authorization": f"Bearer {rev_token}"}
    rev_user = client.get("/users/me", headers=rev_hdr).json()

    app1 = client.post(
        "/approvals",
        headers=admin_hdr,
        json={"decision_id": d1_id, "reviewer_id": rev_user["id"], "approval_level": 1, "comments": "Needs sign-off"}
    ).json()

    client.post(
        f"/approvals/{app1['id']}/approve",
        headers=rev_hdr,
        json={"comments": "Approved after review"}
    )

    # 3. Decision Report Generation & Filtering
    log_step("3. Decision Report API (GET /reports/decisions)", "Test filtering, summaries, pagination, sorting")
    dec_rep = client.get("/reports/decisions", headers=admin_hdr).json()
    print(f"Total Decisions in Report: {dec_rep['total']}")
    print(f"Summary Statistics: {json.dumps(dec_rep['summary'], indent=2)}")
    assert dec_rep["total"] >= 2
    assert dec_rep["summary"]["total_decisions"] >= 2

    # Filtered report
    dec_filt = client.get("/reports/decisions?category=Database%20Architecture", headers=admin_hdr).json()
    assert len(dec_filt["items"]) >= 1
    assert dec_filt["items"][0]["title"] == "Adopt PostgreSQL for Reporting DB"
    print(f"[+] Category Filter verified: Found '{dec_filt['items'][0]['title']}'")

    # 4. Approval Report Generation & Metrics
    log_step("4. Approval Report API (GET /reports/approvals)", "Verify turnaround time and completion metrics")
    app_rep = client.get("/reports/approvals", headers=admin_hdr).json()
    print(f"Total Approvals in Report: {app_rep['total']}")
    print(f"Approval Summary: {json.dumps(app_rep['summary'], indent=2)}")
    assert app_rep["total"] >= 1
    assert app_rep["summary"]["approved_approvals"] >= 1
    assert app_rep["summary"]["approval_completion_rate"] == 100.0
    print(f"[+] Approval turnaround calculation: {app_rep['items'][0]['turnaround_time_hours']} hours")

    # 5. Team Report Generation & Scoping
    log_step("5. Team Report API (GET /reports/teams)", "Verify Department stats and RBAC scoping")
    team_rep = client.get("/reports/teams", headers=admin_hdr).json()
    print(f"Teams Report Summary: {json.dumps(team_rep['summary'], indent=2)}")
    print(f"Teams Items ({len(team_rep['items'])} teams):")
    for t in team_rep["items"]:
        print(f"  - Team '{t['team_name']}': {t['number_of_members']} members, {t['total_decisions']} decisions, {t['team_approval_statistics']['total_approvals']} approvals")
    assert team_rep["summary"]["total_teams"] >= 1

    # 6. Audit Report Generation (Admin Only)
    log_step("6. Audit Report API (GET /reports/audit)", "Verify Audit Trail summary & Admin RBAC")
    # Non-admin forbidden check
    assert client.get("/reports/audit", headers=emp_hdr).status_code == 403
    print("[+] Verified Non-Admin receives 403 Forbidden for Audit Reports")

    audit_rep = client.get("/reports/audit", headers=admin_hdr).json()
    print(f"Total Audit Events: {audit_rep['total']}")
    print(f"Action Breakdown: {audit_rep['summary']['action_breakdown']}")
    assert audit_rep["total"] >= 1

    # 7. PDF Export Endpoints
    log_step("7. PDF Export Endpoints (/reports/*/export/pdf)", "Verify binary stream and PDF magic bytes")
    for name, path in [
        ("Decisions PDF", "/reports/decisions/export/pdf"),
        ("Approvals PDF", "/reports/approvals/export/pdf"),
        ("Teams PDF", "/reports/teams/export/pdf"),
        ("Audit PDF", "/reports/audit/export/pdf"),
    ]:
        resp = client.get(path, headers=admin_hdr)
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        assert resp.content.startswith(b"%PDF-")
        print(f"[+] {name} successfully generated ({len(resp.content)} bytes, starts with %PDF-)")

    # 8. Excel Export Endpoints
    log_step("8. Excel Export Endpoints (/reports/*/export/excel)", "Verify Excel workbook structure and sheets")
    for name, path in [
        ("Decisions Excel", "/reports/decisions/export/excel"),
        ("Approvals Excel", "/reports/approvals/export/excel"),
        ("Teams Excel", "/reports/teams/export/excel"),
        ("Audit Excel", "/reports/audit/export/excel"),
    ]:
        resp = client.get(path, headers=admin_hdr)
        assert resp.status_code == 200
        assert "openxmlformats-officedocument.spreadsheetml.sheet" in resp.headers["content-type"]
        wb = openpyxl.load_workbook(io.BytesIO(resp.content))
        print(f"[+] {name} successfully generated ({len(resp.content)} bytes, Sheets: {wb.sheetnames})")
        assert "Summary & Filters" in wb.sheetnames

    # 9. Error Handling Cases
    log_step("9. Error Handling & Validation Tests (401, 403, 422)", "Verify strict error responses")
    # No JWT -> 401
    assert client.get("/reports/decisions").status_code == 401
    print("[+] 401 Unauthorized verified for missing JWT")

    # Invalid date range -> 422
    assert client.get("/reports/decisions?start_date=2026-12-31&end_date=2026-01-01", headers=admin_hdr).status_code == 422
    print("[+] 422 Validation Error verified for invalid date range")

    # Invalid status -> 422
    assert client.get("/reports/decisions?status=WrongStatus", headers=admin_hdr).status_code == 422
    print("[+] 422 Validation Error verified for invalid status")

    # Invalid sorting -> 422
    assert client.get("/reports/decisions?sort_by=injected_column", headers=admin_hdr).status_code == 422
    print("[+] 422 Validation Error verified for disallowed sorting field")

    print("\n==================================================")
    print("[SUCCESS] ALL SPRINT 12 REPORTING MODULE VERIFICATIONS PASSED!")
    print("==================================================\n")


if __name__ == "__main__":
    run_verification()
