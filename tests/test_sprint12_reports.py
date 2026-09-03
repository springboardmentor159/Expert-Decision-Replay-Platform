from datetime import datetime, timedelta
import io
from fastapi.testclient import TestClient
import openpyxl
import pytest

from app.main import app

client = TestClient(app)


def setup_user(email: str, role: str, department: str = "Enterprise Architecture"):
    u_data = {
        "full_name": email.split("@")[0].replace("_", " ").title(),
        "email": email,
        "role": role,
        "password": "Password123!",
        "employee_id": f"EMP_S12_{email[:7]}",
        "department": department,
        "designation": f"Lead {role}",
        "phone_number": "+1-555-1200"
    }
    client.post("/users", json=u_data)
    login_res = client.post("/auth/login", json={"email": email, "password": "Password123!"})
    assert login_res.status_code == 200, f"Login failed for {email}"
    return login_res.json()["access_token"], login_res.json()["user"]["id"]


@pytest.fixture
def seeded_data():
    # 1. Create Users
    emp_token, emp_id = setup_user("s12_emp@example.com", "Employee", "Architecture")
    rev_token, rev_id = setup_user("s12_rev@example.com", "Reviewer", "Architecture")
    mgr_token, mgr_id = setup_user("s12_mgr@example.com", "Manager", "Architecture")
    adm_token, adm_id = setup_user("s12_adm@example.com", "Administrator", "Compliance")
    other_emp_token, other_emp_id = setup_user("s12_other@example.com", "Employee", "Operations")

    emp_headers = {"Authorization": f"Bearer {emp_token}"}
    adm_headers = {"Authorization": f"Bearer {adm_token}"}
    mgr_headers = {"Authorization": f"Bearer {mgr_token}"}
    rev_headers = {"Authorization": f"Bearer {rev_token}"}
    other_emp_headers = {"Authorization": f"Bearer {other_emp_token}"}

    # 2. Create Decisions
    # Decision 1: Draft Technology
    dec1_res = client.post("/decisions", json={
        "title": "Select Event Streaming Architecture",
        "problem_statement": "Evaluate Kafka vs RabbitMQ for real-time telemetry",
        "category": "Technology"
    }, headers=emp_headers)
    assert dec1_res.status_code == 201
    dec1_id = dec1_res.json()["id"]

    # Add Alternative to Dec 1
    client.post(f"/decisions/{dec1_id}/alternatives", json={
        "title": "Apache Kafka Cluster",
        "description": "High throughput distributed log",
        "pros": "High throughput, retention",
        "cons": "Operational complexity",
        "cost": 15000.0,
        "risk_level": "Medium"
    }, headers=emp_headers)

    # Decision 2: Approved Security
    dec2_res = client.post("/decisions", json={
        "title": "Adopt Zero-Trust Network Access",
        "problem_statement": "Secure remote employee access to internal infrastructure",
        "category": "Security"
    }, headers=emp_headers)
    assert dec2_res.status_code == 201
    dec2_id = dec2_res.json()["id"]

    # Create Approval for Dec 2 and Approve it
    apprv_create = client.post(f"/decisions/{dec2_id}/approvals", json={
        "reviewer_id": rev_id,
        "approval_level": 1,
        "comments": "Please review ZTNA"
    }, headers=emp_headers)
    apprv_id = apprv_create.json()["id"] if apprv_create.status_code == 201 else 1

    client.post(f"/approvals/{apprv_id}/action", json={
        "status": "Approved",
        "comments": "Meets all enterprise security standards"
    }, headers=rev_headers)

    # Update Dec 2 status to Approved
    client.patch(f"/decisions/{dec2_id}/status", json={"status": "Approved"}, headers=emp_headers)

    # Decision 3: Rejected Finance by Other Emp
    dec3_res = client.post("/decisions", json={
        "title": "Migrate ERP to Cloud Provider",
        "problem_statement": "Evaluate cloud migration costs",
        "category": "Finance"
    }, headers=other_emp_headers)
    assert dec3_res.status_code == 201
    dec3_id = dec3_res.json()["id"]
    client.patch(f"/decisions/{dec3_id}/status", json={"status": "Rejected"}, headers=other_emp_headers)

    return {
        "emp_headers": emp_headers,
        "adm_headers": adm_headers,
        "mgr_headers": mgr_headers,
        "rev_headers": rev_headers,
        "other_emp_headers": other_emp_headers,
        "emp_id": emp_id,
        "rev_id": rev_id,
        "dec1_id": dec1_id,
        "dec2_id": dec2_id,
        "dec3_id": dec3_id,
    }


# =============================================================================
# 1. DECISION REPORTS TESTS
# =============================================================================

def test_decision_reports_basic(seeded_data):
    headers = seeded_data["emp_headers"]
    res = client.get("/reports/decisions", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "summary" in data
    assert data["total"] >= 3
    assert data["summary"]["total_decisions"] >= 3
    assert data["summary"]["approved_decisions"] >= 1


def test_decision_reports_filtering(seeded_data):
    headers = seeded_data["emp_headers"]

    # Filter by Category
    res_cat = client.get("/reports/decisions?category=Technology", headers=headers)
    assert res_cat.status_code == 200
    for item in res_cat.json()["items"]:
        assert item["category"] == "Technology"

    # Filter by Status
    res_st = client.get("/reports/decisions?status=Approved", headers=headers)
    assert res_st.status_code == 200
    for item in res_st.json()["items"]:
        assert item["status"] == "Approved"

    # Filter by Created By
    res_user = client.get(f"/reports/decisions?created_by={seeded_data['emp_id']}", headers=headers)
    assert res_user.status_code == 200
    for item in res_user.json()["items"]:
        assert item["created_by"] == seeded_data["emp_id"]

    # Filter by Date Range
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    res_date = client.get(f"/reports/decisions?start_date={today_str}&end_date={today_str}", headers=headers)
    assert res_date.status_code == 200


def test_decision_reports_pagination_and_sorting(seeded_data):
    headers = seeded_data["emp_headers"]

    # Pagination
    res_paged = client.get("/reports/decisions?page=1&page_size=2", headers=headers)
    assert res_paged.status_code == 200
    assert len(res_paged.json()["items"]) <= 2
    assert res_paged.json()["page"] == 1
    assert res_paged.json()["page_size"] == 2

    # Sorting
    res_sorted = client.get("/reports/decisions?sort_by=title&sort_order=asc", headers=headers)
    assert res_sorted.status_code == 200
    titles = [item["title"] for item in res_sorted.json()["items"]]
    assert titles == sorted(titles)


# =============================================================================
# 2. APPROVAL REPORTS TESTS
# =============================================================================

def test_approval_reports_basic_and_filters(seeded_data):
    headers = seeded_data["emp_headers"]
    res = client.get("/reports/approvals", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "summary" in data
    assert "total_approvals" in data["summary"]
    assert "completion_rate" in data["summary"]
    assert "average_turnaround_time_hours" in data["summary"]

    # Filter by Status
    res_apprv = client.get("/reports/approvals?status=Approved", headers=headers)
    assert res_apprv.status_code == 200
    for item in res_apprv.json()["items"]:
        assert item["status"] == "Approved"

    # Filter by Reviewer
    res_rev = client.get(f"/reports/approvals?reviewer_id={seeded_data['rev_id']}", headers=headers)
    assert res_rev.status_code == 200
    for item in res_rev.json()["items"]:
        assert item["reviewer_id"] == seeded_data["rev_id"]


# =============================================================================
# 3. TEAM REPORTS TESTS & RBAC
# =============================================================================

def test_team_reports_admin_access(seeded_data):
    adm_headers = seeded_data["adm_headers"]
    res = client.get("/reports/teams", headers=adm_headers)
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "summary" in data
    assert data["summary"]["total_teams"] >= 2
    dept_names = [t["team_name"] for t in data["items"]]
    assert "Architecture" in dept_names or "Operations" in dept_names


def test_team_reports_department_rbac(seeded_data):
    emp_headers = seeded_data["emp_headers"]

    # Employee in Architecture can view their own team
    res_own = client.get("/reports/teams?team=Architecture", headers=emp_headers)
    assert res_own.status_code == 200
    assert len(res_own.json()["items"]) == 1
    assert res_own.json()["items"][0]["team_name"] == "Architecture"

    # Employee in Architecture cannot view Operations -> 403 Forbidden
    res_forbidden = client.get("/reports/teams?team=Operations", headers=emp_headers)
    assert res_forbidden.status_code == 403


# =============================================================================
# 4. AUDIT REPORTS TESTS & RBAC
# =============================================================================

def test_audit_reports_admin_success(seeded_data):
    adm_headers = seeded_data["adm_headers"]
    res = client.get("/reports/audit", headers=adm_headers)
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "summary" in data
    assert data["summary"]["total_audit_logs"] >= 1
    assert "actions_breakdown" in data["summary"]
    assert "entities_breakdown" in data["summary"]


def test_audit_reports_non_admin_forbidden(seeded_data):
    emp_headers = seeded_data["emp_headers"]
    res = client.get("/reports/audit", headers=emp_headers)
    assert res.status_code == 403

    mgr_headers = seeded_data["mgr_headers"]
    res_mgr = client.get("/reports/audit", headers=mgr_headers)
    assert res_mgr.status_code == 403


# =============================================================================
# 5. PDF & EXCEL EXPORTS TESTS
# =============================================================================

def test_pdf_exports(seeded_data):
    emp_headers = seeded_data["emp_headers"]
    adm_headers = seeded_data["adm_headers"]

    # Decisions PDF
    res_dec_pdf = client.get("/reports/decisions/export/pdf", headers=emp_headers)
    assert res_dec_pdf.status_code == 200
    assert res_dec_pdf.headers["content-type"] == "application/pdf"
    assert res_dec_pdf.content.startswith(b"%PDF-")

    # Approvals PDF
    res_apprv_pdf = client.get("/reports/approvals/export/pdf", headers=emp_headers)
    assert res_apprv_pdf.status_code == 200
    assert res_apprv_pdf.headers["content-type"] == "application/pdf"
    assert res_apprv_pdf.content.startswith(b"%PDF-")

    # Teams PDF
    res_team_pdf = client.get("/reports/teams/export/pdf", headers=adm_headers)
    assert res_team_pdf.status_code == 200
    assert res_team_pdf.headers["content-type"] == "application/pdf"
    assert res_team_pdf.content.startswith(b"%PDF-")

    # Audit PDF (Admin only)
    res_audit_pdf = client.get("/reports/audit/export/pdf", headers=adm_headers)
    assert res_audit_pdf.status_code == 200
    assert res_audit_pdf.headers["content-type"] == "application/pdf"
    assert res_audit_pdf.content.startswith(b"%PDF-")

    # Audit PDF by Employee -> 403 Forbidden
    res_audit_emp_pdf = client.get("/reports/audit/export/pdf", headers=emp_headers)
    assert res_audit_emp_pdf.status_code == 403


def test_excel_exports(seeded_data):
    emp_headers = seeded_data["emp_headers"]
    adm_headers = seeded_data["adm_headers"]

    # Decisions Excel
    res_dec_xlsx = client.get("/reports/decisions/export/excel?status=Approved", headers=emp_headers)
    assert res_dec_xlsx.status_code == 200
    assert "spreadsheetml.sheet" in res_dec_xlsx.headers["content-type"]
    wb = openpyxl.load_workbook(io.BytesIO(res_dec_xlsx.content))
    assert "Decisions Report" in wb.sheetnames

    # Approvals Excel
    res_apprv_xlsx = client.get("/reports/approvals/export/excel", headers=emp_headers)
    assert res_apprv_xlsx.status_code == 200
    wb_apprv = openpyxl.load_workbook(io.BytesIO(res_apprv_xlsx.content))
    assert "Approvals Report" in wb_apprv.sheetnames

    # Teams Excel
    res_team_xlsx = client.get("/reports/teams/export/excel", headers=adm_headers)
    assert res_team_xlsx.status_code == 200
    wb_team = openpyxl.load_workbook(io.BytesIO(res_team_xlsx.content))
    assert "Teams Report" in wb_team.sheetnames

    # Audit Excel (Admin)
    res_audit_xlsx = client.get("/reports/audit/export/excel", headers=adm_headers)
    assert res_audit_xlsx.status_code == 200
    wb_audit = openpyxl.load_workbook(io.BytesIO(res_audit_xlsx.content))
    assert "Audit Report" in wb_audit.sheetnames


# =============================================================================
# 6. ERROR HANDLING & VALIDATIONS TESTS
# =============================================================================

def test_error_handling_unauthenticated():
    # No JWT token -> 401 Unauthorized
    assert client.get("/reports/decisions").status_code == 401
    assert client.get("/reports/approvals").status_code == 401
    assert client.get("/reports/teams").status_code == 401
    assert client.get("/reports/audit").status_code == 401
    assert client.get("/reports/decisions/export/pdf").status_code == 401
    assert client.get("/reports/decisions/export/excel").status_code == 401


def test_error_handling_invalid_inputs(seeded_data):
    headers = seeded_data["emp_headers"]

    # Invalid date format -> 422
    res_bad_date = client.get("/reports/decisions?start_date=invalid-date", headers=headers)
    assert res_bad_date.status_code == 422

    # Invalid date range (start > end) -> 422
    res_bad_range = client.get("/reports/decisions?start_date=2026-12-31&end_date=2026-01-01", headers=headers)
    assert res_bad_range.status_code == 422

    # Invalid status -> 422
    res_bad_status = client.get("/reports/decisions?status=NonExistentStatus", headers=headers)
    assert res_bad_status.status_code == 422

    # Invalid sorting field -> 422
    res_bad_sort = client.get("/reports/decisions?sort_by=malicious_sql_injection", headers=headers)
    assert res_bad_sort.status_code == 422

    # Invalid pagination values -> 422
    res_bad_page = client.get("/reports/decisions?page=0", headers=headers)
    assert res_bad_page.status_code == 422

    res_bad_page_size = client.get("/reports/decisions?page_size=0", headers=headers)
    assert res_bad_page_size.status_code == 422


def test_no_matching_records_empty_result(seeded_data):
    headers = seeded_data["emp_headers"]
    # Non-existent category or future date
    res = client.get("/reports/decisions?start_date=2099-01-01&end_date=2099-12-31", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["summary"]["total_decisions"] == 0
