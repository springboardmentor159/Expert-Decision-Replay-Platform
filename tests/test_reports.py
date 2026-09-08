import math
from datetime import datetime, timedelta

import pytest
from app.core.security import hash_password
from app.models.audit_log import AuditLog
from app.models.decision import Decision
from app.models.enums import AuditAction, AuditEntityType, DecisionStatus, UserRole
from app.models.user import User


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_user(db_session, email, employee_id, role=UserRole.EMPLOYEE, department=None):
    user = User(
        full_name=f"Report User {email.split('@')[0]}",
        email=email,
        role=role,
        password=hash_password("password123"),
        employee_id=employee_id,
        department=department,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _auth_headers(user, make_token):
    return {"Authorization": f"Bearer {make_token(str(user.id))}"}


def _create_decision(client, headers, title="Test Decision", category="Engineering", status_value="Draft"):
    return client.post(
        "/decisions",
        json={"title": title, "problem_statement": "PS", "category": category},
        headers=headers,
    )


def _create_audit_log(db_session, user_id, action, entity_type, entity_id=None, description=None, ip_address=None):
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        ip_address=ip_address,
    )
    db_session.add(entry)
    db_session.commit()
    db_session.refresh(entry)
    return entry


# ===========================================================================
# /reports/decisions
# ===========================================================================

class TestReportDecisions:
    def test_empty_result(self, client, db_session, make_token):
        user = _create_user(db_session, "empty_rpt@example.com", "EMP_EMPTY", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/decisions", headers=headers)
        assert res.status_code == 200
        body = res.json()
        assert body["items"] == []
        assert body["total"] == 0
        assert body["summary"]["total"] == 0

    def test_basic_listing(self, client, db_session, make_token):
        user = _create_user(db_session, "basic_rpt@example.com", "EMP_BASIC", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        _create_decision(client, headers, title="Decision A", category="Engineering")
        _create_decision(client, headers, title="Decision B", category="Marketing")

        res = client.get("/reports/decisions", headers=headers)
        assert res.status_code == 200
        body = res.json()
        assert body["total"] == 2
        assert len(body["items"]) == 2
        titles = {item["title"] for item in body["items"]}
        assert titles == {"Decision A", "Decision B"}

    def test_summary_counts(self, client, db_session, make_token):
        user = _create_user(db_session, "summary_rpt@example.com", "EMP_SUM", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        r1 = _create_decision(client, headers, title="D1").json()
        r2 = _create_decision(client, headers, title="D2").json()
        r3 = _create_decision(client, headers, title="D3").json()
        client.patch(f"/decisions/{r1['id']}/status", json={"status": "Approved"}, headers=headers)
        client.patch(f"/decisions/{r2['id']}/status", json={"status": "Rejected"}, headers=headers)

        res = client.get("/reports/decisions", headers=headers)
        body = res.json()
        summary = body["summary"]
        assert summary["total"] == 3
        assert summary["approved"] == 1
        assert summary["rejected"] == 1
        assert summary["draft"] == 1
        assert summary["under_review"] == 0
        assert summary["archived"] == 0

    def test_filter_by_category(self, client, db_session, make_token):
        user = _create_user(db_session, "cat_rpt@example.com", "EMP_CAT", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        _create_decision(client, headers, category="Engineering")
        _create_decision(client, headers, category="Marketing")
        _create_decision(client, headers, category="Engineering")

        res = client.get("/reports/decisions?category=Engineering", headers=headers)
        assert res.status_code == 200
        assert res.json()["total"] == 2
        assert all(item["category"] == "Engineering" for item in res.json()["items"])

    def test_filter_by_status(self, client, db_session, make_token):
        user = _create_user(db_session, "sts_rpt@example.com", "EMP_STS", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        _create_decision(client, headers, title="Draft1")
        r2 = _create_decision(client, headers, title="Approved1").json()
        client.patch(f"/decisions/{r2['id']}/status", json={"status": "Approved"}, headers=headers)

        res = client.get("/reports/decisions?status=Approved", headers=headers)
        assert res.status_code == 200
        assert res.json()["total"] == 1
        assert res.json()["items"][0]["status"] == "Approved"

    def test_filter_by_creator(self, client, db_session, make_token):
        emp_a = _create_user(db_session, "creator_a_rpt@example.com", "EMP_CA", UserRole.EMPLOYEE)
        emp_b = _create_user(db_session, "creator_b_rpt@example.com", "EMP_CB", UserRole.EMPLOYEE)
        headers_a = _auth_headers(emp_a, make_token)
        headers_b = _auth_headers(emp_b, make_token)
        _create_decision(client, headers_a, title="A's Decision")
        _create_decision(client, headers_b, title="B's Decision")

        admin = _create_user(db_session, "admin_rpt@example.com", "ADM_RPT", UserRole.ADMINISTRATOR)
        admin_headers = _auth_headers(admin, make_token)
        res = client.get(f"/reports/decisions?creator={emp_a.id}", headers=admin_headers)
        assert res.status_code == 200
        assert res.json()["total"] == 1
        assert res.json()["items"][0]["creator"] == emp_a.full_name

    def test_filter_by_date_range(self, client, db_session, make_token):
        user = _create_user(db_session, "date_rpt@example.com", "EMP_DATE", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        _create_decision(client, headers, title="Old Decision")

        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        res = client.get(f"/reports/decisions?start_date={yesterday}&end_date={today}", headers=headers)
        assert res.status_code == 200
        assert res.json()["total"] == 1

    def test_pagination(self, client, db_session, make_token):
        user = _create_user(db_session, "page_rpt@example.com", "EMP_PAGE", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        for i in range(5):
            _create_decision(client, headers, title=f"Decision {i}")

        res = client.get("/reports/decisions?page=1&page_size=2", headers=headers)
        body = res.json()
        assert body["total"] == 5
        assert len(body["items"]) == 2
        assert body["page"] == 1
        assert body["page_size"] == 2
        assert body["pages"] == 3

    def test_sort_by_title(self, client, db_session, make_token):
        user = _create_user(db_session, "sort_rpt@example.com", "EMP_SORT", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        _create_decision(client, headers, title="Charlie")
        _create_decision(client, headers, title="Alpha")
        _create_decision(client, headers, title="Bravo")

        res = client.get("/reports/decisions?sort_by=title&sort_order=asc", headers=headers)
        titles = [item["title"] for item in res.json()["items"]]
        assert titles == ["Alpha", "Bravo", "Charlie"]

    def test_invalid_sort_returns_422(self, client, db_session, make_token):
        user = _create_user(db_session, "isort_rpt@example.com", "EMP_ISORT", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/decisions?sort_by=invalid_field", headers=headers)
        assert res.status_code == 422

    def test_invalid_status_returns_422(self, client, db_session, make_token):
        user = _create_user(db_session, "ists_rpt@example.com", "EMP_ISTS", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/decisions?status=InvalidStatus", headers=headers)
        assert res.status_code == 422

    def test_invalid_date_format_returns_422(self, client, db_session, make_token):
        user = _create_user(db_session, "idate_rpt@example.com", "EMP_IDATE", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/decisions?start_date=not-a-date", headers=headers)
        assert res.status_code == 422

    def test_invalid_date_range_returns_422(self, client, db_session, make_token):
        user = _create_user(db_session, "idrange_rpt@example.com", "EMP_IDR", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/decisions?start_date=2026-12-31&end_date=2026-01-01", headers=headers)
        assert res.status_code == 422

    def test_alternative_count(self, client, db_session, make_token):
        user = _create_user(db_session, "alt_rpt@example.com", "EMP_ALT", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        r = _create_decision(client, headers, title="With Alts").json()
        client.post(f"/decisions/{r['id']}/alternatives", json={"name": "Alt1", "pros": "p", "cons": "c"}, headers=headers)
        client.post(f"/decisions/{r['id']}/alternatives", json={"name": "Alt2", "pros": "p", "cons": "c"}, headers=headers)

        res = client.get("/reports/decisions", headers=headers)
        item = res.json()["items"][0]
        assert item["alternative_count"] == 2
        assert item["tags"] == []

    def test_approval_count(self, client, db_session, make_token):
        user = _create_user(db_session, "acnt_rpt@example.com", "EMP_ACNT", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        r = _create_decision(client, headers, title="Approved Dec").json()
        _create_audit_log(db_session, user.id, "approve", "decision", r["id"], "Approved")

        res = client.get("/reports/decisions", headers=headers)
        item = res.json()["items"][0]
        assert item["approval_count"] == 1

    def test_invalid_page_returns_422(self, client, db_session, make_token):
        user = _create_user(db_session, "ipage_rpt@example.com", "EMP_IPAGE", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/decisions?page=0", headers=headers)
        assert res.status_code == 422

    def test_invalid_page_size_returns_422(self, client, db_session, make_token):
        user = _create_user(db_session, "ips_rpt@example.com", "EMP_IPS", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/decisions?page_size=0", headers=headers)
        assert res.status_code == 422
        res2 = client.get("/reports/decisions?page_size=101", headers=headers)
        assert res2.status_code == 422

    def test_invalid_sort_order_returns_422(self, client, db_session, make_token):
        user = _create_user(db_session, "isor_rpt@example.com", "EMP_ISOR", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/decisions?sort_order=invalid", headers=headers)
        assert res.status_code == 422

    def test_requires_auth(self, client, db_session):
        res = client.get("/reports/decisions")
        assert res.status_code == 401


# ===========================================================================
# /reports/approvals
# ===========================================================================

class TestReportApprovals:
    def test_empty_result(self, client, db_session, make_token):
        user = _create_user(db_session, "aempty_rpt@example.com", "AEMP_EMPTY", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/approvals", headers=headers)
        assert res.status_code == 200
        body = res.json()
        assert body["items"] == []
        assert body["total"] == 0
        assert body["summary"]["total"] == 0
        assert body["summary"]["completion_rate"] == 0.0

    def test_derived_from_audit_logs(self, client, db_session, make_token):
        user = _create_user(db_session, "aderived_rpt@example.com", "AEMP_DER", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        r = _create_decision(client, headers, title="Approve Me").json()
        _create_audit_log(db_session, user.id, "approve", "decision", r["id"], "Approved decision")
        _create_audit_log(db_session, user.id, "reject", "decision", r["id"], "Rejected decision")

        res = client.get("/reports/approvals", headers=headers)
        assert res.status_code == 200
        body = res.json()
        assert body["total"] == 2
        statuses = {item["status"] for item in body["items"]}
        assert statuses == {"Approved", "Rejected"}

    def test_summary_counts(self, client, db_session, make_token):
        user = _create_user(db_session, "asummary_rpt@example.com", "AEMP_SUM", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        r1 = _create_decision(client, headers, title="D1").json()
        r2 = _create_decision(client, headers, title="D2").json()
        _create_audit_log(db_session, user.id, "approve", "decision", r1["id"])
        _create_audit_log(db_session, user.id, "approve", "decision", r2["id"])
        _create_audit_log(db_session, user.id, "reject", "decision", r1["id"])

        res = client.get("/reports/approvals", headers=headers)
        summary = res.json()["summary"]
        assert summary["total"] == 3
        assert summary["approved"] == 2
        assert summary["rejected"] == 1
        assert summary["pending"] == 0
        assert summary["completion_rate"] == 1.0

    def test_filter_by_status(self, client, db_session, make_token):
        user = _create_user(db_session, "asts_rpt@example.com", "AEMP_STS", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        r = _create_decision(client, headers).json()
        _create_audit_log(db_session, user.id, "approve", "decision", r["id"])
        _create_audit_log(db_session, user.id, "reject", "decision", r["id"])

        res = client.get("/reports/approvals?status=approved", headers=headers)
        assert res.status_code == 200
        assert res.json()["total"] == 1
        assert res.json()["items"][0]["status"] == "Approved"

    def test_filter_by_decision(self, client, db_session, make_token):
        user = _create_user(db_session, "adec_rpt@example.com", "AEMP_DEC", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        r1 = _create_decision(client, headers, title="D1").json()
        r2 = _create_decision(client, headers, title="D2").json()
        _create_audit_log(db_session, user.id, "approve", "decision", r1["id"])
        _create_audit_log(db_session, user.id, "reject", "decision", r2["id"])

        res = client.get(f"/reports/approvals?decision={r1['id']}", headers=headers)
        assert res.status_code == 200
        assert res.json()["total"] == 1
        assert res.json()["items"][0]["decision_id"] == r1["id"]

    def test_filter_by_date_range(self, client, db_session, make_token):
        user = _create_user(db_session, "adate_rpt@example.com", "AEMP_DATE", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        r = _create_decision(client, headers).json()
        _create_audit_log(db_session, user.id, "approve", "decision", r["id"])

        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        res = client.get(f"/reports/approvals?start_date={yesterday}&end_date={today}", headers=headers)
        assert res.status_code == 200
        assert res.json()["total"] == 1

    def test_pagination(self, client, db_session, make_token):
        user = _create_user(db_session, "apage_rpt@example.com", "AEMP_PAGE", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        r = _create_decision(client, headers).json()
        for _ in range(5):
            _create_audit_log(db_session, user.id, "approve", "decision", r["id"])

        res = client.get("/reports/approvals?page=1&page_size=2", headers=headers)
        body = res.json()
        assert body["total"] == 5
        assert len(body["items"]) == 2
        assert body["pages"] == 3

    def test_sort_by_created_date(self, client, db_session, make_token):
        user = _create_user(db_session, "asort_rpt@example.com", "AEMP_SORT", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        r = _create_decision(client, headers).json()
        _create_audit_log(db_session, user.id, "approve", "decision", r["id"])
        _create_audit_log(db_session, user.id, "reject", "decision", r["id"])

        res = client.get("/reports/approvals?sort_by=created_date&sort_order=asc", headers=headers)
        assert res.status_code == 200
        assert res.json()["total"] == 2

    def test_invalid_status_returns_422(self, client, db_session, make_token):
        user = _create_user(db_session, "aists_rpt@example.com", "AEMP_ISTS", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/approvals?status=invalid", headers=headers)
        assert res.status_code == 422

    def test_invalid_sort_returns_422(self, client, db_session, make_token):
        user = _create_user(db_session, "aisort_rpt@example.com", "AEMP_ISORT", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/approvals?sort_by=nonexistent", headers=headers)
        assert res.status_code == 422

    def test_invalid_date_returns_422(self, client, db_session, make_token):
        user = _create_user(db_session, "aidate_rpt@example.com", "AEMP_IDATE", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/approvals?start_date=bad-date", headers=headers)
        assert res.status_code == 422

    def test_invalid_date_range_returns_422(self, client, db_session, make_token):
        user = _create_user(db_session, "aidrange_rpt@example.com", "AEMP_IDR", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/approvals?start_date=2026-12-31&end_date=2026-01-01", headers=headers)
        assert res.status_code == 422

    def test_requires_auth(self, client, db_session):
        res = client.get("/reports/approvals")
        assert res.status_code == 401

    def test_employee_sees_own_approvals_only(self, client, db_session, make_token):
        emp_a = _create_user(db_session, "aown_a_rpt@example.com", "AEMP_OA", UserRole.EMPLOYEE)
        emp_b = _create_user(db_session, "aown_b_rpt@example.com", "AEMP_OB", UserRole.EMPLOYEE)
        headers_a = _auth_headers(emp_a, make_token)
        headers_b = _auth_headers(emp_b, make_token)

        r = _create_decision(client, headers_a).json()
        _create_audit_log(db_session, emp_a.id, "approve", "decision", r["id"])
        _create_audit_log(db_session, emp_b.id, "reject", "decision", r["id"])

        res_a = client.get("/reports/approvals", headers=headers_a)
        assert res_a.json()["total"] == 1
        assert res_a.json()["items"][0]["status"] == "Approved"

        res_b = client.get("/reports/approvals", headers=headers_b)
        assert res_b.json()["total"] == 1
        assert res_b.json()["items"][0]["status"] == "Rejected"


# ===========================================================================
# /reports/teams
# ===========================================================================

class TestReportTeams:
    def test_empty_result(self, client, db_session, make_token):
        user = _create_user(db_session, "tempty_rpt@example.com", "TEMP_EMPTY", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/teams", headers=headers)
        assert res.status_code == 200
        body = res.json()
        assert body["items"] == []
        assert body["total"] == 0

    def test_groups_by_department(self, client, db_session, make_token):
        _create_user(db_session, "teng_rpt@example.com", "TEMP_ENG", UserRole.EMPLOYEE, department="Engineering")
        _create_user(db_session, "teng2_rpt@example.com", "TEMP_ENG2", UserRole.EMPLOYEE, department="Engineering")
        _create_user(db_session, "tmark_rpt@example.com", "TEMP_MARK", UserRole.EMPLOYEE, department="Marketing")

        admin = _create_user(db_session, "tadmin_rpt@example.com", "TEMP_ADM", UserRole.ADMINISTRATOR)
        headers = _auth_headers(admin, make_token)

        # Create decisions for Engineering users
        eng_headers = _auth_headers(
            db_session.query(User).filter(User.email == "teng_rpt@example.com").first(), make_token
        )
        _create_decision(client, eng_headers, title="Eng Decision")

        res = client.get("/reports/teams", headers=headers)
        body = res.json()
        assert body["total"] == 2
        teams = {item["team"]: item for item in body["items"]}
        assert teams["Engineering"]["member_count"] == 2
        assert teams["Engineering"]["decision_count"] == 1
        assert teams["Marketing"]["member_count"] == 1
        assert teams["Marketing"]["decision_count"] == 0

    def test_filter_by_team(self, client, db_session, make_token):
        _create_user(db_session, "tfeng_rpt@example.com", "TEMP_FENG", UserRole.EMPLOYEE, department="Engineering")
        _create_user(db_session, "tfmark_rpt@example.com", "TEMP_FMARK", UserRole.EMPLOYEE, department="Marketing")

        admin = _create_user(db_session, "tfadmin_rpt@example.com", "TEMP_FADM", UserRole.ADMINISTRATOR)
        headers = _auth_headers(admin, make_token)

        res = client.get("/reports/teams?team=Engineering", headers=headers)
        body = res.json()
        assert body["total"] == 1
        assert body["items"][0]["team"] == "Engineering"

    def test_approval_stats(self, client, db_session, make_token):
        emp = _create_user(db_session, "tapp_rpt@example.com", "TEMP_APP", UserRole.EMPLOYEE, department="Engineering")
        admin = _create_user(db_session, "tappadm_rpt@example.com", "TEMP_APPADM", UserRole.ADMINISTRATOR)
        headers = _auth_headers(admin, make_token)
        emp_headers = _auth_headers(emp, make_token)

        r = _create_decision(client, emp_headers).json()
        _create_audit_log(db_session, admin.id, "approve", "decision", r["id"])
        _create_audit_log(db_session, admin.id, "reject", "decision", r["id"])

        res = client.get("/reports/teams", headers=headers)
        team = res.json()["items"][0]
        assert team["approval_stats"]["approved"] == 1
        assert team["approval_stats"]["rejected"] == 1
        assert team["approval_stats"]["pending"] == 0

    def test_filter_by_date_range(self, client, db_session, make_token):
        _create_user(db_session, "tdate_rpt@example.com", "TEMP_DATE", UserRole.EMPLOYEE, department="Engineering")
        admin = _create_user(db_session, "tdateadm_rpt@example.com", "TEMP_DATEADM", UserRole.ADMINISTRATOR)
        headers = _auth_headers(admin, make_token)

        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        res = client.get(f"/reports/teams?start_date={yesterday}&end_date={today}", headers=headers)
        assert res.status_code == 200

    def test_sort_by_team_name(self, client, db_session, make_token):
        _create_user(db_session, "tsort1_rpt@example.com", "TEMP_S1", UserRole.EMPLOYEE, department="Zebra")
        _create_user(db_session, "tsort2_rpt@example.com", "TEMP_S2", UserRole.EMPLOYEE, department="Alpha")

        admin = _create_user(db_session, "tsortadm_rpt@example.com", "TEMP_SADM", UserRole.ADMINISTRATOR)
        headers = _auth_headers(admin, make_token)

        res = client.get("/reports/teams?sort_by=team_name&sort_order=asc", headers=headers)
        teams = [item["team"] for item in res.json()["items"]]
        assert teams == ["Alpha", "Zebra"]

    def test_invalid_sort_returns_422(self, client, db_session, make_token):
        user = _create_user(db_session, "tisort_rpt@example.com", "TEMP_ISORT", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/teams?sort_by=invalid_field", headers=headers)
        assert res.status_code == 422

    def test_invalid_date_returns_422(self, client, db_session, make_token):
        user = _create_user(db_session, "tidate_rpt@example.com", "TEMP_IDATE", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/teams?start_date=bad", headers=headers)
        assert res.status_code == 422

    def test_invalid_date_range_returns_422(self, client, db_session, make_token):
        user = _create_user(db_session, "tidrange_rpt@example.com", "TEMP_IDR", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/teams?start_date=2026-12-31&end_date=2026-01-01", headers=headers)
        assert res.status_code == 422

    def test_requires_auth(self, client, db_session):
        res = client.get("/reports/teams")
        assert res.status_code == 401


# ===========================================================================
# /reports/audit
# ===========================================================================

class TestReportAudit:
    def test_empty_result(self, client, db_session, make_token):
        user = _create_user(db_session, "uempty_rpt@example.com", "UEMP_EMPTY", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/audit", headers=headers)
        assert res.status_code == 200
        body = res.json()
        assert body["items"] == []
        assert body["total"] == 0

    def test_basic_listing(self, client, db_session, make_token):
        user = _create_user(db_session, "ubasic_rpt@example.com", "UEMP_BASIC", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        log1 = _create_audit_log(db_session, user.id, "create", "decision", 1, "Created decision")
        log2 = _create_audit_log(db_session, user.id, "update", "decision", 1, "Updated decision")

        res = client.get("/reports/audit", headers=headers)
        body = res.json()
        assert body["total"] == 2
        assert len(body["items"]) == 2
        actions = {item["action"] for item in body["items"]}
        assert actions == {"create", "update"}

    def test_filter_by_user(self, client, db_session, make_token):
        emp_a = _create_user(db_session, "ufilt_a_rpt@example.com", "UEMP_FA", UserRole.EMPLOYEE)
        emp_b = _create_user(db_session, "ufilt_b_rpt@example.com", "UEMP_FB", UserRole.EMPLOYEE)
        _create_audit_log(db_session, emp_a.id, "create", "decision", 1, "A created")
        _create_audit_log(db_session, emp_b.id, "create", "decision", 2, "B created")

        admin = _create_user(db_session, "ufiltadm_rpt@example.com", "UEMP_FADM", UserRole.ADMINISTRATOR)
        headers = _auth_headers(admin, make_token)

        res = client.get(f"/reports/audit?user={emp_a.id}", headers=headers)
        assert res.json()["total"] == 1
        assert res.json()["items"][0]["user"] == emp_a.full_name

    def test_filter_by_action(self, client, db_session, make_token):
        user = _create_user(db_session, "uact_rpt@example.com", "UEMP_ACT", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        _create_audit_log(db_session, user.id, "create", "decision", 1)
        _create_audit_log(db_session, user.id, "update", "decision", 1)
        _create_audit_log(db_session, user.id, "delete", "alternative", 1)

        res = client.get("/reports/audit?action=create", headers=headers)
        assert res.json()["total"] == 1
        assert res.json()["items"][0]["action"] == "create"

    def test_filter_by_entity_type(self, client, db_session, make_token):
        user = _create_user(db_session, "uet_rpt@example.com", "UEMP_ET", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        _create_audit_log(db_session, user.id, "create", "decision", 1)
        _create_audit_log(db_session, user.id, "create", "comment", 1)

        res = client.get("/reports/audit?entity_type=decision", headers=headers)
        assert res.json()["total"] == 1

    def test_filter_by_entity_id(self, client, db_session, make_token):
        user = _create_user(db_session, "ueid_rpt@example.com", "UEMP_EID", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        _create_audit_log(db_session, user.id, "create", "decision", 42)
        _create_audit_log(db_session, user.id, "create", "decision", 99)

        res = client.get("/reports/audit?entity_id=42", headers=headers)
        assert res.json()["total"] == 1

    def test_filter_by_date_range(self, client, db_session, make_token):
        user = _create_user(db_session, "udate_rpt@example.com", "UEMP_DATE", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        _create_audit_log(db_session, user.id, "create", "decision", 1)

        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        res = client.get(f"/reports/audit?start_date={yesterday}&end_date={today}", headers=headers)
        assert res.status_code == 200
        assert res.json()["total"] == 1

    def test_pagination(self, client, db_session, make_token):
        user = _create_user(db_session, "upage_rpt@example.com", "UEMP_PAGE", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        for i in range(5):
            _create_audit_log(db_session, user.id, "create", "decision", i)

        res = client.get("/reports/audit?page=1&page_size=2", headers=headers)
        body = res.json()
        assert body["total"] == 5
        assert len(body["items"]) == 2
        assert body["pages"] == 3

    def test_sort_by_created_date(self, client, db_session, make_token):
        user = _create_user(db_session, "usort_rpt@example.com", "UEMP_SORT", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        _create_audit_log(db_session, user.id, "create", "decision", 1)
        _create_audit_log(db_session, user.id, "update", "decision", 1)

        res = client.get("/reports/audit?sort_by=created_date&sort_order=asc", headers=headers)
        assert res.status_code == 200
        assert res.json()["total"] == 2

    def test_employee_scoped_to_own(self, client, db_session, make_token):
        emp_a = _create_user(db_session, "uown_a_rpt@example.com", "UEMP_OA", UserRole.EMPLOYEE)
        emp_b = _create_user(db_session, "uown_b_rpt@example.com", "UEMP_OB", UserRole.EMPLOYEE)
        _create_audit_log(db_session, emp_a.id, "create", "decision", 1)
        _create_audit_log(db_session, emp_b.id, "create", "decision", 2)

        headers_a = _auth_headers(emp_a, make_token)
        res = client.get("/reports/audit", headers=headers_a)
        assert res.json()["total"] == 1
        assert res.json()["items"][0]["user"] == emp_a.full_name

    def test_manager_sees_all(self, client, db_session, make_token):
        mgr = _create_user(db_session, "umgr_rpt@example.com", "UEMP_MGR", UserRole.MANAGER)
        emp = _create_user(db_session, "umgremp_rpt@example.com", "UEMP_MGREMP", UserRole.EMPLOYEE)
        _create_audit_log(db_session, mgr.id, "create", "decision", 1)
        _create_audit_log(db_session, emp.id, "create", "decision", 2)

        headers = _auth_headers(mgr, make_token)
        res = client.get("/reports/audit", headers=headers)
        assert res.json()["total"] == 2

    def test_invalid_action_returns_422(self, client, db_session, make_token):
        user = _create_user(db_session, "uiact_rpt@example.com", "UEMP_IACT", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/audit?action=invalid_action", headers=headers)
        assert res.status_code == 422

    def test_invalid_entity_type_returns_422(self, client, db_session, make_token):
        user = _create_user(db_session, "uiet_rpt@example.com", "UEMP_IET", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/audit?entity_type=invalid_type", headers=headers)
        assert res.status_code == 422

    def test_invalid_sort_returns_422(self, client, db_session, make_token):
        user = _create_user(db_session, "uisort_rpt@example.com", "UEMP_ISORT", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/audit?sort_by=nonexistent", headers=headers)
        assert res.status_code == 422

    def test_invalid_date_returns_422(self, client, db_session, make_token):
        user = _create_user(db_session, "uidate_rpt@example.com", "UEMP_IDATE", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/audit?start_date=bad-date", headers=headers)
        assert res.status_code == 422

    def test_invalid_date_range_returns_422(self, client, db_session, make_token):
        user = _create_user(db_session, "uidrange_rpt@example.com", "UEMP_IDR", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/audit?start_date=2026-12-31&end_date=2026-01-01", headers=headers)
        assert res.status_code == 422

    def test_invalid_page_returns_422(self, client, db_session, make_token):
        user = _create_user(db_session, "uipage_rpt@example.com", "UEMP_IPAGE", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/audit?page=0", headers=headers)
        assert res.status_code == 422

    def test_invalid_page_size_returns_422(self, client, db_session, make_token):
        user = _create_user(db_session, "uips_rpt@example.com", "UEMP_IPS", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        res = client.get("/reports/audit?page_size=0", headers=headers)
        assert res.status_code == 422
        res2 = client.get("/reports/audit?page_size=101", headers=headers)
        assert res2.status_code == 422

    def test_requires_auth(self, client, db_session):
        res = client.get("/reports/audit")
        assert res.status_code == 401

    def test_ip_address_included(self, client, db_session, make_token):
        user = _create_user(db_session, "uip_rpt@example.com", "UEMP_IP", UserRole.ADMINISTRATOR)
        headers = _auth_headers(user, make_token)
        _create_audit_log(db_session, user.id, "create", "decision", 1, ip_address="192.168.1.1")

        res = client.get("/reports/audit", headers=headers)
        item = res.json()["items"][0]
        assert item["ip_address"] == "192.168.1.1"
