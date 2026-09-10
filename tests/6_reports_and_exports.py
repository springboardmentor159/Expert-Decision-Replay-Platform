from fastapi.testclient import TestClient


def test_reports_and_filtering(client: TestClient, admin_headers: dict):
    """
    Test Reports (Sprint 13 Section 17):
    - Decision Reports
    - Approval Reports
    - Team Reports
    - Audit Reports
    """
    # 1. Decision Reports with filtering
    res = client.get("/reports/decisions?page=1&page_size=10", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "summary" in data
    assert "items" in data
    assert "total" in data

    # 2. Approval Reports
    res = client.get("/reports/approvals?page=1&page_size=10", headers=admin_headers)
    assert res.status_code == 200
    assert "summary" in res.json()

    # 3. Team Reports
    res = client.get("/reports/teams?page=1&page_size=10", headers=admin_headers)
    assert res.status_code == 200
    assert "summary" in res.json()

    # 4. Audit Reports (Admin only)
    res = client.get("/reports/audit?page=1&page_size=10", headers=admin_headers)
    assert res.status_code == 200
    assert "summary" in res.json()


def test_pdf_export(client: TestClient, admin_headers: dict):
    """
    Test PDF Generation (Sprint 13 Section 18):
    Verify that generated PDF files start with '%PDF-' header and have correct headers.
    """
    pdf_endpoints = [
        "/reports/decisions/export/pdf",
        "/reports/approvals/export/pdf",
        "/reports/teams/export/pdf",
        "/reports/audit/export/pdf",
    ]
    for ep in pdf_endpoints:
        res = client.get(ep, headers=admin_headers)
        assert res.status_code == 200, f"PDF export failed for {ep}: {res.status_code}"
        assert res.headers["content-type"] == "application/pdf"
        assert res.content.startswith(b"%PDF-"), f"Corrupted PDF binary format from {ep}"


def test_excel_export(client: TestClient, admin_headers: dict):
    """
    Test Excel Export (Sprint 13 Section 19):
    Verify that generated Excel files start with 'PK' ZIP archive header and have correct MIME type.
    """
    excel_endpoints = [
        "/reports/decisions/export/excel",
        "/reports/approvals/export/excel",
        "/reports/teams/export/excel",
        "/reports/audit/export/excel",
    ]
    for ep in excel_endpoints:
        res = client.get(ep, headers=admin_headers)
        assert res.status_code == 200, f"Excel export failed for {ep}: {res.status_code}"
        assert "spreadsheetml" in res.headers["content-type"]
        assert res.content.startswith(b"PK\x03\x04"), f"Invalid Excel xlsx binary format from {ep}"


def test_role_based_and_self_scoped_reports(
    client: TestClient,
    admin_headers: dict,
    employee_headers: dict,
    employee_user,
):
    """
    Verify role-based and self-scoping in reports and decision listings:
    - Employee is restricted to their own authored decisions in /reports/decisions
    - Admin can view all decisions in /reports/decisions
    - Filter by created_by in /decisions works correctly
    """
    # 1. Employee creates a decision
    create_res = client.post(
        "/decisions",
        json={
            "title": "Employee Private Decision Scope Test",
            "problem_statement": "Testing role-based and self-scoping reports",
            "category": "Architecture",
        },
        headers=employee_headers,
    )
    assert create_res.status_code == 201
    created_id = create_res.json()["id"]

    # 2. Employee queries decision reports
    emp_report = client.get("/reports/decisions", headers=employee_headers)
    assert emp_report.status_code == 200
    emp_data = emp_report.json()
    for item in emp_data["items"]:
        assert item["created_by"] == employee_user.id

    # 3. Employee exports PDF with self-scope
    emp_pdf = client.get("/reports/decisions/export/pdf", headers=employee_headers)
    assert emp_pdf.status_code == 200
    assert emp_pdf.headers["content-type"] == "application/pdf"
    assert emp_pdf.content.startswith(b"%PDF-")

    # 4. Admin queries decision reports - total must be >= employee's items
    admin_report = client.get("/reports/decisions", headers=admin_headers)
    assert admin_report.status_code == 200
    admin_data = admin_report.json()
    assert admin_data["total"] >= emp_data["total"]

    # 5. Query /decisions?created_by={employee_user.id}
    filtered_res = client.get(f"/decisions?created_by={employee_user.id}", headers=admin_headers)
    assert filtered_res.status_code == 200
    for d in filtered_res.json()["items"]:
        assert d["created_by"] == employee_user.id

