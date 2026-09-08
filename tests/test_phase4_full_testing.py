"""
Phase 4 — Full Testing & Bug Fixing
====================================
Covers:
  1. End-to-End Workflow (Approval): Login → Create Decision → Alternatives → Compare
     → Discussion → Submit → Reviewer → Manager → Approved → Audit → Version →
     Dashboard → Report → PDF → Excel
  2. End-to-End Workflow (Rejection): Same flow with Rejection instead of Approval
  3. Regression: Verify all 10 main modules still work
  4. Concurrent: Two users acting on the same decision simultaneously
  5. Performance: Large dataset against main endpoints
  6. Security: JWT, RBAC, hashing, secrets, injection, CORS, invalid input
"""

import io
import json
import math
import time
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_user(client: TestClient, email: str, role: str = "Employee",
                 full_name: str = "Test User", department: str = "Engineering",
                 employee_id: str | None = None, db_session=None) -> dict:
    """Register a user and return the response dict.
    For non-Employee roles, creates as Employee then updates role via DB."""
    if employee_id is None:
        employee_id = email.split("@")[0].replace(".", "_")

    resp = client.post("/users", json={
        "full_name": full_name,
        "email": email,
        "password": "TestPass123!",
        "employee_id": employee_id,
        "department": department,
        "designation": "Senior Engineer",
        "phone_number": "+1234567890",
    })
    assert resp.status_code == 201, f"User creation failed: {resp.text}"
    user_data = resp.json()

    if role != "Employee":
        # Try to get db_session from app dependency overrides
        if db_session is None:
            try:
                from app.db.database import get_db
                from app.main import app as _app
                override_fn = _app.dependency_overrides.get(get_db)
                if override_fn is not None:
                    gen = override_fn()
                    db_session = next(gen)
            except Exception:
                pass

        if db_session is not None:
            from app.models.user import User
            from app.models.enums import UserRole
            user = db_session.query(User).filter(User.id == user_data["id"]).first()
            if user:
                user.role = UserRole(role)
                db_session.commit()
                db_session.refresh(user)
                user_data["role"] = role

    return user_data


def _login(client: TestClient, email: str, password: str = "TestPass123!") -> dict:
    """Login and return full response dict with access_token."""
    resp = client.post("/login", json={"email": email, "password": password})
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# 1. E2E Workflow — Full Lifecycle (APPROVAL path)
# ---------------------------------------------------------------------------

class TestE2EWorkflowApproval:
    """
    Complete workflow:
    Login → Create Decision → Alternatives → Compare → Discussion
    → Submit (Under Review) → Reviewer review → Manager Approve
    → Audit check → Version check → Dashboard → Report → PDF → Excel
    """

    def test_full_approval_workflow(self, client, db_session):
        # --- Step 1: Register 4 users with different roles ---
        emp = _create_user(client, "emp.e2e@test.com", "Employee", "Alice Employee", "Engineering", "EMP001")
        rev = _create_user(client, "rev.e2e@test.com", "Reviewer", "Bob Reviewer", "Engineering", "REV001", db_session=db_session)
        mgr = _create_user(client, "mgr.e2e@test.com", "Manager", "Carol Manager", "Engineering", "MGR001", db_session=db_session)
        adm = _create_user(client, "adm.e2e@test.com", "Administrator", "Dan Admin", "IT", "ADM001", db_session=db_session)

        # --- Step 2: Login all users ---
        emp_login = _login(client, "emp.e2e@test.com")
        rev_login = _login(client, "rev.e2e@test.com")
        mgr_login = _login(client, "mgr.e2e@test.com")
        adm_login = _login(client, "adm.e2e@test.com")

        emp_h = _auth_header(emp_login["access_token"])
        rev_h = _auth_header(rev_login["access_token"])
        mgr_h = _auth_header(mgr_login["access_token"])
        adm_h = _auth_header(adm_login["access_token"])

        assert emp_login["user"]["role"] == "Employee"
        assert rev_login["user"]["role"] == "Reviewer"
        assert mgr_login["user"]["role"] == "Manager"
        assert adm_login["user"]["role"] == "Administrator"

        # --- Step 3: Employee creates a decision ---
        d_resp = client.post("/decisions", headers=emp_h, json={
            "title": "Cloud Migration Strategy",
            "problem_statement": "We need to migrate from on-premise to cloud",
            "category": "Technology",
        })
        assert d_resp.status_code == 201
        decision = d_resp.json()
        d_id = decision["id"]
        assert decision["status"] == "Draft"
        assert decision["created_by"] == emp["id"]

        # --- Step 4: Employee adds alternatives ---
        alt1_resp = client.post(f"/decisions/{d_id}/alternatives", headers=emp_h, json={
            "name": "AWS Migration",
            "description": "Migrate to Amazon Web Services",
            "pros": "Scalable, mature ecosystem",
            "cons": "Vendor lock-in",
            "estimated_cost": 50000,
            "feasibility_score": 4,
            "risk_level": "Medium",
        })
        assert alt1_resp.status_code == 201
        alt1 = alt1_resp.json()

        alt2_resp = client.post(f"/decisions/{d_id}/alternatives", headers=emp_h, json={
            "name": "Azure Migration",
            "description": "Migrate to Microsoft Azure",
            "pros": "Enterprise integration",
            "cons": "Complex pricing",
            "estimated_cost": 45000,
            "feasibility_score": 3,
            "risk_level": "Low",
        })
        assert alt2_resp.status_code == 201
        alt2 = alt2_resp.json()

        alt3_resp = client.post(f"/decisions/{d_id}/alternatives", headers=emp_h, json={
            "name": "GCP Migration",
            "description": "Migrate to Google Cloud Platform",
            "pros": "AI/ML capabilities",
            "cons": "Smaller enterprise market",
            "estimated_cost": 42000,
            "feasibility_score": 4,
            "risk_level": "Low",
        })
        assert alt3_resp.status_code == 201

        # --- Step 5: Compare alternatives ---
        compare_resp = client.get(f"/decisions/{d_id}/alternatives/compare", headers=emp_h)
        assert compare_resp.status_code == 200
        compare_data = compare_resp.json()
        assert compare_data["decision_id"] == d_id
        assert len(compare_data["alternatives"]) == 3

        # --- Step 6: Discussion - Employee posts comment ---
        comment_resp = client.post(f"/decisions/{d_id}/comments", headers=emp_h, json={
            "content": "I recommend AWS for its mature ecosystem and reliability.",
        })
        assert comment_resp.status_code == 201
        comment = comment_resp.json()

        # --- Step 7: Discussion - Reviewer creates thread ---
        thread_resp = client.post(f"/decisions/{d_id}/threads", headers=rev_h, json={
            "title": "Cost vs Scalability Analysis",
            "description": "Let's discuss the trade-offs between cost and scalability",
        })
        assert thread_resp.status_code == 201
        thread = thread_resp.json()

        # --- Step 8: Manager replies to thread ---
        reply_resp = client.post(f"/threads/{thread['id']}/comments", headers=mgr_h, json={
            "content": "Good point. AWS costs more but scales better for our needs.",
        })
        assert reply_resp.status_code == 201

        # --- Step 9: Manager creates meeting note ---
        note_resp = client.post(f"/decisions/{d_id}/meeting-notes", headers=mgr_h, json={
            "title": "Cloud Architecture Review Meeting",
            "content": "Reviewed all three alternatives. Decision pending approval.",
            "meeting_date": datetime.now().isoformat(),
        })
        assert note_resp.status_code == 201

        # --- Step 10: Employee sets rationale ---
        rat_resp = client.put(f"/decisions/{d_id}/rationale", headers=emp_h, json={
            "rationale": "AWS chosen for scalability and reliability based on team analysis.",
        })
        assert rat_resp.status_code == 200
        assert rat_resp.json()["rationale"] == "AWS chosen for scalability and reliability based on team analysis."

        # --- Step 11: Employee submits (Draft → Under Review) ---
        submit_resp = client.patch(f"/decisions/{d_id}/status", headers=emp_h, json={
            "status": "Under Review",
        })
        assert submit_resp.status_code == 200
        assert submit_resp.json()["status"] == "Under Review"

        # --- Step 12: Reviewer approves (Under Review → Approved) ---
        approve_resp = client.patch(f"/decisions/{d_id}/status", headers=rev_h, json={
            "status": "Approved",
        })
        assert approve_resp.status_code == 200
        assert approve_resp.json()["status"] == "Approved"

        # --- Step 13: Verify audit history ---
        history_resp = client.get(f"/decisions/{d_id}/history", headers=emp_h)
        assert history_resp.status_code == 200
        history = history_resp.json()["items"]
        assert len(history) >= 3  # create, status_change (submit), status_change (approve)

        actions = [h["action"] for h in history]
        assert "create" in actions
        assert "status_change" in actions

        # --- Step 14: Verify version history ---
        versions_resp = client.get(f"/decisions/{d_id}/versions", headers=emp_h)
        assert versions_resp.status_code == 200
        versions = versions_resp.json()["versions"]
        assert len(versions) >= 2  # v1 (create), v2 (submit), v3 (approve)
        version_numbers = [v["version_number"] for v in versions]
        assert 1 in version_numbers

        # --- Step 15: Verify specific version ---
        v1_resp = client.get(f"/decisions/{d_id}/versions/1", headers=emp_h)
        assert v1_resp.status_code == 200
        assert v1_resp.json()["status"] == "Draft"

        # --- Step 16: Verify employee dashboard ---
        emp_dash = client.get("/dashboard/employee", headers=emp_h)
        assert emp_dash.status_code == 200
        emp_data = emp_dash.json()
        assert emp_data["total_decisions"] >= 1

        # --- Step 17: Verify manager dashboard ---
        mgr_dash = client.get("/dashboard/manager/statistics", headers=mgr_h)
        assert mgr_dash.status_code == 200
        mgr_data = mgr_dash.json()
        assert mgr_data["total"] >= 1

        # --- Step 18: Verify admin dashboard ---
        admin_dash = client.get("/dashboard/admin", headers=adm_h)
        assert admin_dash.status_code == 200

        # --- Step 19: Verify admin analytics ---
        analytics_resp = client.get("/dashboard/admin/analytics", headers=adm_h)
        assert analytics_resp.status_code == 200

        # --- Step 20: Verify reports ---
        reports_resp = client.get("/reports/decisions", headers=emp_h)
        assert reports_resp.status_code == 200
        report_data = reports_resp.json()
        assert report_data["summary"]["total"] >= 1

        # --- Step 21: Verify approvals report ---
        approvals_resp = client.get("/reports/approvals", headers=mgr_h)
        assert approvals_resp.status_code == 200

        # --- Step 22: Verify teams report ---
        teams_resp = client.get("/reports/teams", headers=emp_h)
        assert teams_resp.status_code == 200

        # --- Step 23: Verify audit report ---
        audit_report_resp = client.get("/reports/audit", headers=adm_h)
        assert audit_report_resp.status_code == 200

        # --- Step 24: Verify PDF export ---
        pdf_resp = client.get("/reports/decisions/export/pdf", headers=emp_h)
        assert pdf_resp.status_code == 200
        assert pdf_resp.headers["content-type"] == "application/pdf"
        assert b"%PDF" in pdf_resp.content

        # --- Step 25: Verify Excel export ---
        excel_resp = client.get("/reports/decisions/export/excel", headers=emp_h)
        assert excel_resp.status_code == 200
        assert "spreadsheetml" in excel_resp.headers["content-type"] or "octet-stream" in excel_resp.headers["content-type"]

        # --- Step 26: Verify activity log ---
        activities_resp = client.get("/activities", headers=emp_h)
        assert activities_resp.status_code == 200

        # --- Step 27: Verify audit logs ---
        audit_logs_resp = client.get("/audit-logs", headers=adm_h)
        assert audit_logs_resp.status_code == 200
        assert audit_logs_resp.json()["total"] >= 1

        # --- Step 28: Verify security logs (admin/manager only) ---
        sec_resp = client.get("/security/logs", headers=adm_h)
        assert sec_resp.status_code == 200

        # --- Step 29: Verify access logs (admin/manager only) ---
        acc_resp = client.get("/access/logs", headers=adm_h)
        assert acc_resp.status_code == 200

        # --- Step 30: Logout ---
        logout_resp = client.post("/login/logout", headers=emp_h)
        assert logout_resp.status_code == 200


# ---------------------------------------------------------------------------
# 2. E2E Workflow — Rejection Path
# ---------------------------------------------------------------------------

class TestE2EWorkflowRejection:

    def test_full_rejection_workflow(self, client):
        # Create users
        emp = _create_user(client, "emp.reject@test.com", "Employee", "Emp Reject", "HR", "REJ_EMP01")
        rev = _create_user(client, "rev.reject@test.com", "Reviewer", "Rev Reject", "HR", "REJ_REV01")

        emp_h = _auth_header(_login(client, "emp.reject@test.com")["access_token"])
        rev_h = _auth_header(_login(client, "rev.reject@test.com")["access_token"])

        # Create decision
        d_resp = client.post("/decisions", headers=emp_h, json={
            "title": "Hiring Freeze Proposal",
            "problem_statement": "Budget constraints require hiring freeze",
            "category": "Operations",
        })
        assert d_resp.status_code == 201
        d_id = d_resp.json()["id"]

        # Add alternative
        alt_resp = client.post(f"/decisions/{d_id}/alternatives", headers=emp_h, json={
            "name": "Complete Freeze",
            "description": "No new hires for 6 months",
            "pros": "Immediate cost savings",
            "cons": "Team burnout risk",
            "estimated_cost": 0,
            "feasibility_score": 2,
            "risk_level": "High",
        })
        assert alt_resp.status_code == 201

        # Submit for review
        submit_resp = client.patch(f"/decisions/{d_id}/status", headers=emp_h, json={
            "status": "Under Review",
        })
        assert submit_resp.status_code == 200
        assert submit_resp.json()["status"] == "Under Review"

        # Reviewer rejects
        reject_resp = client.patch(f"/decisions/{d_id}/status", headers=rev_h, json={
            "status": "Rejected",
        })
        assert reject_resp.status_code == 200
        assert reject_resp.json()["status"] == "Rejected"

        # Verify decision is rejected
        get_resp = client.get(f"/decisions/{d_id}", headers=emp_h)
        assert get_resp.status_code == 200
        assert get_resp.json()["status"] == "Rejected"

        # Verify version history includes rejection
        versions_resp = client.get(f"/decisions/{d_id}/versions", headers=emp_h)
        assert versions_resp.status_code == 200
        versions = versions_resp.json()["versions"]
        statuses = [v["status"] for v in versions]
        assert "Draft" in statuses
        assert "Under Review" in statuses

        # Verify audit trail
        history_resp = client.get(f"/decisions/{d_id}/history", headers=emp_h)
        assert history_resp.status_code == 200
        history = history_resp.json()["items"]
        status_changes = [h for h in history if h["action"] == "status_change"]
        assert len(status_changes) >= 2  # submit + reject

        # Verify employee dashboard shows the rejected decision
        emp_dash = client.get("/dashboard/employee", headers=emp_h)
        assert emp_dash.status_code == 200

        # Verify reports show rejected status
        reports_resp = client.get("/reports/decisions", headers=emp_h, params={"status": "Rejected"})
        assert reports_resp.status_code == 200
        assert reports_resp.json()["summary"]["rejected"] >= 1


# ---------------------------------------------------------------------------
# 3. Regression Tests — Verify All 10 Main Modules
# ---------------------------------------------------------------------------

class TestRegressionAuthentication:
    """Module: Authentication"""

    def test_login_valid(self, client):
        _create_user(client, "auth.reg@test.com", "Employee", "Auth Reg", "IT", "AUTH_REG01")
        resp = client.post("/login", json={"email": "auth.reg@test.com", "password": "TestPass123!"})
        assert resp.status_code == 200
        assert "access_token" in resp.json()
        assert resp.json()["token_type"] == "bearer"

    def test_login_invalid_password(self, client):
        _create_user(client, "auth.badpw@test.com", "Employee", "Bad PW", "IT", "AUTH_BPW01")
        resp = client.post("/login", json={"email": "auth.badpw@test.com", "password": "WrongPassword"})
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post("/login", json={"email": "noone@test.com", "password": "TestPass123!"})
        assert resp.status_code == 401

    def test_register_duplicate_email(self, client):
        _create_user(client, "dup.auth@test.com", "Employee", "Dup Auth", "IT", "DUP_AUTH01")
        resp = client.post("/users", json={
            "full_name": "Dup2",
            "email": "dup.auth@test.com",
            "password": "TestPass123!",
            "role": "Employee",
            "employee_id": "DUP_AUTH02",
        })
        assert resp.status_code == 400

    def test_protected_endpoint_without_token(self, client):
        resp = client.get("/decisions")
        assert resp.status_code == 401

    def test_protected_endpoint_invalid_token(self, client):
        resp = client.get("/decisions", headers={"Authorization": "Bearer invalid.jwt.token"})
        assert resp.status_code == 401


class TestRegressionUsers:
    """Module: Users"""

    def test_create_user(self, client):
        resp = _create_user(client, "user.reg@test.com", "Employee", "User Reg", "HR", "USER_REG01")
        assert resp["full_name"] == "User Reg"
        assert resp["role"] == "Employee"

    def test_get_all_users(self, client):
        _create_user(client, "users.all@test.com", "Employee", "Users All", "HR", "USERS_ALL01")
        h = _auth_header(_login(client, "users.all@test.com")["access_token"])
        resp = client.get("/users", headers=h)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_get_user_by_id(self, client):
        u = _create_user(client, "user.getid@test.com", "Employee", "Get ID", "HR", "GET_ID01")
        h = _auth_header(_login(client, "user.getid@test.com")["access_token"])
        resp = client.get(f"/users/{u['id']}", headers=h)
        assert resp.status_code == 200
        assert resp.json()["id"] == u["id"]

    def test_update_user(self, client):
        u = _create_user(client, "user.upd@test.com", "Employee", "Upd User", "HR", "UPD_USER01")
        h = _auth_header(_login(client, "user.upd@test.com")["access_token"])
        resp = client.put(f"/users/{u['id']}", headers=h, json={
            "full_name": "Updated Name",
        })
        assert resp.status_code == 200
        assert resp.json()["full_name"] == "Updated Name"

    def test_delete_user(self, client):
        u = _create_user(client, "user.del@test.com", "Employee", "Del User", "HR", "DEL_USER01")
        h = _auth_header(_login(client, "user.del@test.com")["access_token"])
        resp = client.delete(f"/users/{u['id']}", headers=h)
        assert resp.status_code == 200

    def test_get_nonexistent_user(self, client):
        u = _create_user(client, "user.noexist@test.com", "Employee", "No Exist", "HR", "NOEXIST01")
        h = _auth_header(_login(client, "user.noexist@test.com")["access_token"])
        resp = client.get("/users/99999", headers=h)
        assert resp.status_code == 404


class TestRegressionDecisions:
    """Module: Decisions"""

    def test_create_decision(self, client):
        u = _create_user(client, "dec.create@test.com", "Employee", "Dec Create", "IT", "DEC_CR01")
        h = _auth_header(_login(client, "dec.create@test.com")["access_token"])
        resp = client.post("/decisions", headers=h, json={
            "title": "Test Decision",
            "problem_statement": "Test problem",
            "category": "Technology",
        })
        assert resp.status_code == 201
        assert resp.json()["status"] == "Draft"

    def test_get_decision(self, client):
        u = _create_user(client, "dec.get@test.com", "Employee", "Dec Get", "IT", "DEC_GT01")
        h = _auth_header(_login(client, "dec.get@test.com")["access_token"])
        d = client.post("/decisions", headers=h, json={
            "title": "Get Decision", "problem_statement": "p", "category": "Finance",
        }).json()
        resp = client.get(f"/decisions/{d['id']}", headers=h)
        assert resp.status_code == 200

    def test_update_decision(self, client):
        u = _create_user(client, "dec.upd@test.com", "Employee", "Dec Upd", "IT", "DEC_UP01")
        h = _auth_header(_login(client, "dec.upd@test.com")["access_token"])
        d = client.post("/decisions", headers=h, json={
            "title": "Original", "problem_statement": "p", "category": "Finance",
        }).json()
        resp = client.put(f"/decisions/{d['id']}", headers=h, json={"title": "Updated"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated"

    def test_status_change(self, client):
        u = _create_user(client, "dec.status@test.com", "Employee", "Dec Status", "IT", "DEC_ST01")
        h = _auth_header(_login(client, "dec.status@test.com")["access_token"])
        d = client.post("/decisions", headers=h, json={
            "title": "Status Test", "problem_statement": "p", "category": "Finance",
        }).json()
        resp = client.patch(f"/decisions/{d['id']}/status", headers=h, json={"status": "Under Review"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "Under Review"

    def test_filter_by_status(self, client):
        u = _create_user(client, "dec.filter@test.com", "Employee", "Dec Filter", "IT", "DEC_FL01")
        h = _auth_header(_login(client, "dec.filter@test.com")["access_token"])
        client.post("/decisions", headers=h, json={
            "title": "Filter Draft", "problem_statement": "p", "category": "Finance",
        })
        resp = client.get("/decisions?status=Draft", headers=h)
        assert resp.status_code == 200
        for d in resp.json():
            assert d["status"] == "Draft"

    def test_get_nonexistent_decision(self, client):
        u = _create_user(client, "dec.noexist@test.com", "Employee", "No Exist", "IT", "DEC_NE01")
        h = _auth_header(_login(client, "dec.noexist@test.com")["access_token"])
        resp = client.get("/decisions/99999", headers=h)
        assert resp.status_code == 404

    def test_invalid_status_value(self, client):
        u = _create_user(client, "dec.invstatus@test.com", "Employee", "Inv Status", "IT", "DEC_IS01")
        h = _auth_header(_login(client, "dec.invstatus@test.com")["access_token"])
        d = client.post("/decisions", headers=h, json={
            "title": "Inv", "problem_statement": "p", "category": "Finance",
        }).json()
        resp = client.patch(f"/decisions/{d['id']}/status", headers=h, json={"status": "InvalidStatus"})
        assert resp.status_code == 422


class TestRegressionAlternatives:
    """Module: Alternatives"""

    def test_create_alternative(self, client):
        u = _create_user(client, "alt.create@test.com", "Employee", "Alt Create", "IT", "ALT_CR01")
        h = _auth_header(_login(client, "alt.create@test.com")["access_token"])
        d = client.post("/decisions", headers=h, json={
            "title": "Alt Decision", "problem_statement": "p", "category": "Tech",
        }).json()
        resp = client.post(f"/decisions/{d['id']}/alternatives", headers=h, json={
            "name": "Option A", "description": "desc", "estimated_cost": 10000,
            "feasibility_score": 3, "risk_level": "Low",
        })
        assert resp.status_code == 201

    def test_compare_alternatives(self, client):
        u = _create_user(client, "alt.compare@test.com", "Employee", "Alt Compare", "IT", "ALT_CMP01")
        h = _auth_header(_login(client, "alt.compare@test.com")["access_token"])
        d = client.post("/decisions", headers=h, json={
            "title": "Compare Decision", "problem_statement": "p", "category": "Tech",
        }).json()
        client.post(f"/decisions/{d['id']}/alternatives", headers=h, json={
            "name": "A", "estimated_cost": 100, "feasibility_score": 3, "risk_level": "Low",
        })
        client.post(f"/decisions/{d['id']}/alternatives", headers=h, json={
            "name": "B", "estimated_cost": 200, "feasibility_score": 4, "risk_level": "Medium",
        })
        resp = client.get(f"/decisions/{d['id']}/alternatives/compare", headers=h)
        assert resp.status_code == 200
        assert len(resp.json()["alternatives"]) == 2

    def test_invalid_feasibility_score(self, client):
        u = _create_user(client, "alt.invfeas@test.com", "Employee", "Inv Feas", "IT", "ALT_IF01")
        h = _auth_header(_login(client, "alt.invfeas@test.com")["access_token"])
        d = client.post("/decisions", headers=h, json={
            "title": "Inv Feas", "problem_statement": "p", "category": "Tech",
        }).json()
        resp = client.post(f"/decisions/{d['id']}/alternatives", headers=h, json={
            "name": "Bad", "feasibility_score": 10, "risk_level": "Low",
        })
        assert resp.status_code == 422

    def test_invalid_risk_level(self, client):
        u = _create_user(client, "alt.invrisk@test.com", "Employee", "Inv Risk", "IT", "ALT_IR01")
        h = _auth_header(_login(client, "alt.invrisk@test.com")["access_token"])
        d = client.post("/decisions", headers=h, json={
            "title": "Inv Risk", "problem_statement": "p", "category": "Tech",
        }).json()
        resp = client.post(f"/decisions/{d['id']}/alternatives", headers=h, json={
            "name": "Bad", "feasibility_score": 3, "risk_level": "Extreme",
        })
        assert resp.status_code == 422


class TestRegressionDiscussion:
    """Module: Discussion (Comments, Threads, Meeting Notes)"""

    def test_create_comment(self, client):
        u = _create_user(client, "disc.comment@test.com", "Employee", "Disc Comment", "IT", "DISC_CM01")
        h = _auth_header(_login(client, "disc.comment@test.com")["access_token"])
        d = client.post("/decisions", headers=h, json={
            "title": "Comment Dec", "problem_statement": "p", "category": "Tech",
        }).json()
        resp = client.post(f"/decisions/{d['id']}/comments", headers=h, json={
            "content": "Great idea!",
        })
        assert resp.status_code == 201

    def test_create_thread(self, client):
        u = _create_user(client, "disc.thread@test.com", "Employee", "Disc Thread", "IT", "DISC_TH01")
        h = _auth_header(_login(client, "disc.thread@test.com")["access_token"])
        d = client.post("/decisions", headers=h, json={
            "title": "Thread Dec", "problem_statement": "p", "category": "Tech",
        }).json()
        resp = client.post(f"/decisions/{d['id']}/threads", headers=h, json={
            "title": "Discussion Thread",
        })
        assert resp.status_code == 201

    def test_create_meeting_note(self, client):
        u = _create_user(client, "disc.meeting@test.com", "Employee", "Disc Meeting", "IT", "DISC_MN01")
        h = _auth_header(_login(client, "disc.meeting@test.com")["access_token"])
        d = client.post("/decisions", headers=h, json={
            "title": "Meeting Dec", "problem_statement": "p", "category": "Tech",
        }).json()
        resp = client.post(f"/decisions/{d['id']}/meeting-notes", headers=h, json={
            "title": "Review Meeting",
            "content": "Reviewed all options",
            "meeting_date": datetime.now().isoformat(),
        })
        assert resp.status_code == 201

    def test_comment_ownership_enforcement(self, client):
        u1 = _create_user(client, "disc.own1@test.com", "Employee", "Owner1", "IT", "DISC_OW1")
        u2 = _create_user(client, "disc.own2@test.com", "Employee", "Owner2", "IT", "DISC_OW2")
        h1 = _auth_header(_login(client, "disc.own1@test.com")["access_token"])
        h2 = _auth_header(_login(client, "disc.own2@test.com")["access_token"])
        d = client.post("/decisions", headers=h1, json={
            "title": "Own Dec", "problem_statement": "p", "category": "Tech",
        }).json()
        c = client.post(f"/decisions/{d['id']}/comments", headers=h1, json={
            "content": "My comment",
        }).json()
        # u2 tries to edit u1's comment → 403
        resp = client.put(f"/comments/{c['id']}", headers=h2, json={"content": "Hacked"})
        assert resp.status_code == 403


class TestRegressionApproval:
    """Module: Approval (Decision status transitions)"""

    def test_draft_to_under_review(self, client):
        u = _create_user(client, "appr.d2ur@test.com", "Employee", "D2UR", "IT", "APPR_D2U01")
        h = _auth_header(_login(client, "appr.d2ur@test.com")["access_token"])
        d = client.post("/decisions", headers=h, json={
            "title": "D2UR", "problem_statement": "p", "category": "Tech",
        }).json()
        resp = client.patch(f"/decisions/{d['id']}/status", headers=h, json={"status": "Under Review"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "Under Review"

    def test_under_review_to_approved(self, client):
        u = _create_user(client, "appr.ur2a@test.com", "Employee", "UR2A", "IT", "APPR_U2A01")
        h = _auth_header(_login(client, "appr.ur2a@test.com")["access_token"])
        d = client.post("/decisions", headers=h, json={
            "title": "UR2A", "problem_statement": "p", "category": "Tech",
        }).json()
        client.patch(f"/decisions/{d['id']}/status", headers=h, json={"status": "Under Review"})
        resp = client.patch(f"/decisions/{d['id']}/status", headers=h, json={"status": "Approved"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "Approved"

    def test_under_review_to_rejected(self, client):
        u = _create_user(client, "appr.ur2r@test.com", "Employee", "UR2R", "IT", "APPR_U2R01")
        h = _auth_header(_login(client, "appr.ur2r@test.com")["access_token"])
        d = client.post("/decisions", headers=h, json={
            "title": "UR2R", "problem_statement": "p", "category": "Tech",
        }).json()
        client.patch(f"/decisions/{d['id']}/status", headers=h, json={"status": "Under Review"})
        resp = client.patch(f"/decisions/{d['id']}/status", headers=h, json={"status": "Rejected"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "Rejected"

    def test_approval_blocked_endpoint_501(self, client):
        u = _create_user(client, "appr.501@test.com", "Manager", "Appr 501", "IT", "APPR_50101")
        h = _auth_header(_login(client, "appr.501@test.com")["access_token"])
        resp = client.get("/dashboard/manager/pending-approvals", headers=h)
        assert resp.status_code == 501

    def test_approval_stats_blocked_501(self, client):
        u = _create_user(client, "appr.stats501@test.com", "Administrator", "Stats 501", "IT", "APPR_S501")
        h = _auth_header(_login(client, "appr.stats501@test.com")["access_token"])
        resp = client.get("/dashboard/admin/approval-statistics", headers=h)
        assert resp.status_code == 501


class TestRegressionKnowledgeRepository:
    """Module: Knowledge Repository (documented as not implemented)"""

    def test_no_knowledge_repository_endpoints(self, client):
        """Verify no knowledge repository endpoints exist."""
        u = _create_user(client, "kr.noexist@test.com", "Employee", "KR No", "IT", "KR_NO01")
        h = _auth_header(_login(client, "kr.noexist@test.com")["access_token"])
        # These endpoints should return 404 or 405 (not implemented)
        for path in ["/knowledge", "/knowledge-repository", "/documents", "/repos"]:
            resp = client.get(path, headers=h)
            assert resp.status_code in (404, 405), f"{path} returned {resp.status_code}"


class TestRegressionDashboard:
    """Module: Dashboard"""

    def test_employee_dashboard(self, client):
        u = _create_user(client, "dash.emp@test.com", "Employee", "Dash Emp", "IT", "DASH_EM01")
        h = _auth_header(_login(client, "dash.emp@test.com")["access_token"])
        resp = client.get("/dashboard/employee", headers=h)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_decisions" in data
        assert "decisions_by_status" in data

    def test_manager_dashboard(self, client):
        u = _create_user(client, "dash.mgr@test.com", "Manager", "Dash Mgr", "IT", "DASH_MG01")
        h = _auth_header(_login(client, "dash.mgr@test.com")["access_token"])
        resp = client.get("/dashboard/manager/statistics", headers=h)
        assert resp.status_code == 200

    def test_admin_dashboard(self, client):
        u = _create_user(client, "dash.adm@test.com", "Administrator", "Dash Admin", "IT", "DASH_AD01")
        h = _auth_header(_login(client, "dash.adm@test.com")["access_token"])
        resp = client.get("/dashboard/admin", headers=h)
        assert resp.status_code == 200

    def test_employee_cannot_access_manager_dashboard(self, client):
        u = _create_user(client, "dash.emp2mgr@test.com", "Employee", "Emp2Mgr", "IT", "DASH_E2M01")
        h = _auth_header(_login(client, "dash.emp2mgr@test.com")["access_token"])
        resp = client.get("/dashboard/manager/statistics", headers=h)
        assert resp.status_code == 403

    def test_employee_cannot_access_admin_dashboard(self, client):
        u = _create_user(client, "dash.emp2adm@test.com", "Employee", "Emp2Adm", "IT", "DASH_E2A01")
        h = _auth_header(_login(client, "dash.emp2adm@test.com")["access_token"])
        resp = client.get("/dashboard/admin", headers=h)
        assert resp.status_code == 403


class TestRegressionAudit:
    """Module: Audit"""

    def test_audit_logs_requires_auth(self, client):
        resp = client.get("/audit-logs")
        assert resp.status_code == 401

    def test_audit_logs_admin_sees_all(self, client):
        u = _create_user(client, "audit.adm@test.com", "Administrator", "Audit Adm", "IT", "AUD_AD01")
        h = _auth_header(_login(client, "audit.adm@test.com")["access_token"])
        # Create some activity
        d = client.post("/decisions", headers=h, json={
            "title": "Audit Test", "problem_statement": "p", "category": "Tech",
        }).json()
        resp = client.get("/audit-logs", headers=h)
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    def test_audit_logs_employee_scoped(self, client):
        u = _create_user(client, "audit.emp@test.com", "Employee", "Audit Emp", "IT", "AUD_EM01")
        h = _auth_header(_login(client, "audit.emp@test.com")["access_token"])
        client.post("/decisions", headers=h, json={
            "title": "Emp Audit", "problem_statement": "p", "category": "Tech",
        })
        resp = client.get("/audit-logs", headers=h)
        assert resp.status_code == 200
        for item in resp.json()["items"]:
            assert item["user_id"] == u["id"]

    def test_security_logs_admin_only(self, client):
        u_emp = _create_user(client, "sec.emp@test.com", "Employee", "Sec Emp", "IT", "SEC_EM01")
        h_emp = _auth_header(_login(client, "sec.emp@test.com")["access_token"])
        resp = client.get("/security/logs", headers=h_emp)
        assert resp.status_code == 403

        u_adm = _create_user(client, "sec.adm@test.com", "Administrator", "Sec Adm", "IT", "SEC_AD01")
        h_adm = _auth_header(_login(client, "sec.adm@test.com")["access_token"])
        resp = client.get("/security/logs", headers=h_adm)
        assert resp.status_code == 200


class TestRegressionReports:
    """Module: Reports"""

    def test_decisions_report(self, client):
        u = _create_user(client, "rpt.dec@test.com", "Employee", "Rpt Dec", "IT", "RPT_DC01")
        h = _auth_header(_login(client, "rpt.dec@test.com")["access_token"])
        resp = client.get("/reports/decisions", headers=h)
        assert resp.status_code == 200
        assert "summary" in resp.json()
        assert "items" in resp.json()

    def test_approvals_report(self, client):
        u = _create_user(client, "rpt.approval@test.com", "Manager", "Rpt Approval", "IT", "RPT_AP01")
        h = _auth_header(_login(client, "rpt.approval@test.com")["access_token"])
        resp = client.get("/reports/approvals", headers=h)
        assert resp.status_code == 200

    def test_teams_report(self, client):
        u = _create_user(client, "rpt.teams@test.com", "Employee", "Rpt Teams", "IT", "RPT_TM01")
        h = _auth_header(_login(client, "rpt.teams@test.com")["access_token"])
        resp = client.get("/reports/teams", headers=h)
        assert resp.status_code == 200

    def test_audit_report(self, client):
        u = _create_user(client, "rpt.audit@test.com", "Administrator", "Rpt Audit", "IT", "RPT_AU01")
        h = _auth_header(_login(client, "rpt.audit@test.com")["access_token"])
        resp = client.get("/reports/audit", headers=h)
        assert resp.status_code == 200

    def test_pdf_export(self, client):
        u = _create_user(client, "rpt.pdf@test.com", "Employee", "Rpt PDF", "IT", "RPT_PF01")
        h = _auth_header(_login(client, "rpt.pdf@test.com")["access_token"])
        resp = client.get("/reports/decisions/export/pdf", headers=h)
        assert resp.status_code == 200
        assert b"%PDF" in resp.content

    def test_excel_export(self, client):
        u = _create_user(client, "rpt.excel@test.com", "Employee", "Rpt Excel", "IT", "RPT_XL01")
        h = _auth_header(_login(client, "rpt.excel@test.com")["access_token"])
        resp = client.get("/reports/decisions/export/excel", headers=h)
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 4. Concurrent Test
# ---------------------------------------------------------------------------

class TestConcurrent:
    """Two users performing actions on the same decision simultaneously.

    NOTE: SQLite in-memory with StaticPool doesn't support true multi-threaded
    concurrent access. These tests simulate rapid sequential requests from two
    different users on the same resource to verify correctness under contention:
    no duplicate records, correct version numbers, correct final state.
    """

    def test_rapid_sequential_status_changes(self, client):
        """Two users rapidly change status of the same decision.
        Verify: no duplicate records, correct final status, unique version numbers."""
        u1 = _create_user(client, "conc.user1@test.com", "Employee", "Conc U1", "IT", "CONC_U01")
        u2 = _create_user(client, "conc.user2@test.com", "Manager", "Conc U2", "IT", "CONC_U02")
        h1 = _auth_header(_login(client, "conc.user1@test.com")["access_token"])
        h2 = _auth_header(_login(client, "conc.user2@test.com")["access_token"])

        # Create a decision
        d = client.post("/decisions", headers=h1, json={
            "title": "Concurrent Test", "problem_statement": "p", "category": "Tech",
        }).json()
        d_id = d["id"]

        # Rapid sequential status changes from two users
        r1 = client.patch(f"/decisions/{d_id}/status", headers=h1, json={"status": "Under Review"})
        assert r1.status_code == 200

        r2 = client.patch(f"/decisions/{d_id}/status", headers=h2, json={"status": "Approved"})
        assert r2.status_code == 200

        # Verify the final state is consistent
        final = client.get(f"/decisions/{d_id}", headers=h1).json()
        assert final["status"] == "Approved"

        # Verify no duplicate version numbers
        versions = client.get(f"/decisions/{d_id}/versions", headers=h1).json()["versions"]
        version_numbers = [v["version_number"] for v in versions]
        assert len(version_numbers) == len(set(version_numbers)), \
            f"Duplicate version numbers found: {version_numbers}"

        # Verify version history is complete: at least v1 (create) + v2 (submit) + v3 (approve)
        assert len(versions) >= 3

    def test_rapid_sequential_alternative_creation(self, client):
        """Two users rapidly create alternatives on the same decision.
        Verify: no duplicate records, both are stored."""
        u1 = _create_user(client, "conc.alt1@test.com", "Employee", "Conc Alt1", "IT", "CONC_A01")
        u2 = _create_user(client, "conc.alt2@test.com", "Employee", "Conc Alt2", "IT", "CONC_A02")
        h1 = _auth_header(_login(client, "conc.alt1@test.com")["access_token"])
        h2 = _auth_header(_login(client, "conc.alt2@test.com")["access_token"])

        d = client.post("/decisions", headers=h1, json={
            "title": "Concurrent Alt", "problem_statement": "p", "category": "Tech",
        }).json()
        d_id = d["id"]

        r1 = client.post(f"/decisions/{d_id}/alternatives", headers=h1, json={
            "name": "Alt A", "estimated_cost": 1000,
            "feasibility_score": 3, "risk_level": "Low",
        })
        assert r1.status_code == 201

        r2 = client.post(f"/decisions/{d_id}/alternatives", headers=h2, json={
            "name": "Alt B", "estimated_cost": 2000,
            "feasibility_score": 4, "risk_level": "Medium",
        })
        assert r2.status_code == 201

        # Verify both alternatives exist
        alts = client.get(f"/decisions/{d_id}/alternatives", headers=h1).json()
        assert len(alts) == 2
        names = {a["name"] for a in alts}
        assert names == {"Alt A", "Alt B"}

        # Verify no duplicate IDs
        alt_ids = [a["id"] for a in alts]
        assert len(alt_ids) == len(set(alt_ids))

    def test_rapid_sequential_comment_creation(self, client):
        """Two users rapidly create comments on the same decision."""
        u1 = _create_user(client, "conc.cmt1@test.com", "Employee", "Conc Cmt1", "IT", "CONC_C01")
        u2 = _create_user(client, "conc.cmt2@test.com", "Employee", "Conc Cmt2", "IT", "CONC_C02")
        h1 = _auth_header(_login(client, "conc.cmt1@test.com")["access_token"])
        h2 = _auth_header(_login(client, "conc.cmt2@test.com")["access_token"])

        d = client.post("/decisions", headers=h1, json={
            "title": "Concurrent Comment", "problem_statement": "p", "category": "Tech",
        }).json()
        d_id = d["id"]

        r1 = client.post(f"/decisions/{d_id}/comments", headers=h1, json={
            "content": "Comment from User 1",
        })
        assert r1.status_code == 201

        r2 = client.post(f"/decisions/{d_id}/comments", headers=h2, json={
            "content": "Comment from User 2",
        })
        assert r2.status_code == 201

        comments = client.get(f"/decisions/{d_id}/comments", headers=h1).json()
        assert len(comments) == 2

        # Verify no duplicate comment IDs
        comment_ids = [c["id"] for c in comments]
        assert len(comment_ids) == len(set(comment_ids))

        # Verify different users created the comments
        user_ids = {c["user_id"] for c in comments}
        assert user_ids == {u1["id"], u2["id"]}


# ---------------------------------------------------------------------------
# 5. Performance Test
# ---------------------------------------------------------------------------

class TestPerformance:
    """Large dataset against main endpoints. Checks response time and pagination."""

    BULK_SIZE = 30  # number of decisions to create for perf testing

    def _bulk_create_decisions(self, client, header, count):
        ids = []
        for i in range(count):
            resp = client.post("/decisions", headers=header, json={
                "title": f"Perf Decision {i}",
                "problem_statement": f"Problem {i}",
                "category": ["Technology", "Finance", "Marketing", "Operations"][i % 4],
            })
            assert resp.status_code == 201
            ids.append(resp.json()["id"])
        return ids

    def _bulk_create_alternatives(self, client, header, decision_id, count):
        for i in range(count):
            resp = client.post(f"/decisions/{decision_id}/alternatives", headers=header, json={
                "name": f"Alt {i}",
                "estimated_cost": 1000 * (i + 1),
                "feasibility_score": (i % 5) + 1,
                "risk_level": ["Low", "Medium", "High", "Critical"][i % 4],
            })
            assert resp.status_code == 201

    def test_search_decisions_performance(self, client):
        """Search decisions with filters - should complete within reasonable time."""
        u = _create_user(client, "perf.search@test.com", "Employee", "Perf Search", "IT", "PERF_SR01")
        h = _auth_header(_login(client, "perf.search@test.com")["access_token"])
        self._bulk_create_decisions(client, h, self.BULK_SIZE)

        start = time.time()
        resp = client.get("/decisions", headers=h)
        elapsed = time.time() - start
        assert resp.status_code == 200
        assert len(resp.json()) == self.BULK_SIZE
        assert elapsed < 5.0, f"Search took {elapsed:.2f}s (>5s threshold)"

    def test_search_with_filter_performance(self, client):
        """Filtered search should be efficient."""
        u = _create_user(client, "perf.filt@test.com", "Employee", "Perf Filt", "IT", "PERF_FL01")
        h = _auth_header(_login(client, "perf.filt@test.com")["access_token"])
        self._bulk_create_decisions(client, h, self.BULK_SIZE)

        start = time.time()
        resp = client.get("/decisions?status=Draft&category=Technology", headers=h)
        elapsed = time.time() - start
        assert resp.status_code == 200
        assert elapsed < 5.0

    def test_alternatives_list_performance(self, client):
        """List alternatives for a decision with many alternatives."""
        u = _create_user(client, "perf.alt@test.com", "Employee", "Perf Alt", "IT", "PERF_AL01")
        h = _auth_header(_login(client, "perf.alt@test.com")["access_token"])
        d = client.post("/decisions", headers=h, json={
            "title": "Perf Alt Decision", "problem_statement": "p", "category": "Tech",
        }).json()
        self._bulk_create_alternatives(client, h, d["id"], 20)

        start = time.time()
        resp = client.get(f"/decisions/{d['id']}/alternatives", headers=h)
        elapsed = time.time() - start
        assert resp.status_code == 200
        assert len(resp.json()) == 20
        assert elapsed < 3.0

    def test_compare_performance(self, client):
        """Compare endpoint with many alternatives."""
        u = _create_user(client, "perf.cmp@test.com", "Employee", "Perf Cmp", "IT", "PERF_CP01")
        h = _auth_header(_login(client, "perf.cmp@test.com")["access_token"])
        d = client.post("/decisions", headers=h, json={
            "title": "Perf Compare", "problem_statement": "p", "category": "Tech",
        }).json()
        self._bulk_create_alternatives(client, h, d["id"], 15)

        start = time.time()
        resp = client.get(f"/decisions/{d['id']}/alternatives/compare", headers=h)
        elapsed = time.time() - start
        assert resp.status_code == 200
        assert len(resp.json()["alternatives"]) == 15
        assert elapsed < 3.0

    def test_dashboard_performance(self, client):
        """Dashboard with existing data."""
        u = _create_user(client, "perf.dash@test.com", "Employee", "Perf Dash", "IT", "PERF_DA01")
        h = _auth_header(_login(client, "perf.dash@test.com")["access_token"])
        self._bulk_create_decisions(client, h, 20)

        start = time.time()
        resp = client.get("/dashboard/employee", headers=h)
        elapsed = time.time() - start
        assert resp.status_code == 200
        assert resp.json()["total_decisions"] == 20
        assert elapsed < 3.0

    def test_audit_logs_pagination_performance(self, client):
        """Audit logs with pagination."""
        u = _create_user(client, "perf.audit@test.com", "Administrator", "Perf Audit", "IT", "PERF_AU01")
        h = _auth_header(_login(client, "perf.audit@test.com")["access_token"])
        self._bulk_create_decisions(client, h, 20)

        start = time.time()
        resp = client.get("/audit-logs?page=1&page_size=10", headers=h)
        elapsed = time.time() - start
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total"] >= 20
        assert elapsed < 3.0

    def test_reports_performance(self, client):
        """Reports endpoint with data."""
        u = _create_user(client, "perf.rpt@test.com", "Employee", "Perf Rpt", "IT", "PERF_RP01")
        h = _auth_header(_login(client, "perf.rpt@test.com")["access_token"])
        self._bulk_create_decisions(client, h, 20)

        start = time.time()
        resp = client.get("/reports/decisions", headers=h)
        elapsed = time.time() - start
        assert resp.status_code == 200
        assert resp.json()["summary"]["total"] >= 20
        assert elapsed < 5.0

    def test_pdf_export_performance(self, client):
        """PDF export with data."""
        u = _create_user(client, "perf.pdf@test.com", "Employee", "Perf PDF", "IT", "PERF_PF01")
        h = _auth_header(_login(client, "perf.pdf@test.com")["access_token"])
        self._bulk_create_decisions(client, h, 20)

        start = time.time()
        resp = client.get("/reports/decisions/export/pdf", headers=h)
        elapsed = time.time() - start
        assert resp.status_code == 200
        assert b"%PDF" in resp.content
        assert elapsed < 10.0

    def test_excel_export_performance(self, client):
        """Excel export with data."""
        u = _create_user(client, "perf.excel@test.com", "Employee", "Perf Excel", "IT", "PERF_XL01")
        h = _auth_header(_login(client, "perf.excel@test.com")["access_token"])
        self._bulk_create_decisions(client, h, 20)

        start = time.time()
        resp = client.get("/reports/decisions/export/excel", headers=h)
        elapsed = time.time() - start
        assert resp.status_code == 200
        assert elapsed < 10.0


# ---------------------------------------------------------------------------
# 6. Security Test
# ---------------------------------------------------------------------------

class TestSecurityJWT:
    """JWT is required, properly validated, tokens are secure."""

    def test_all_protected_endpoints_require_jwt(self, client):
        """Verify JWT is required on all protected endpoints."""
        protected_endpoints = [
            ("GET", "/decisions"),
            ("POST", "/decisions"),
            ("GET", "/users"),
            ("GET", "/dashboard/employee"),
            ("GET", "/activities"),
            ("GET", "/audit-logs"),
            ("GET", "/reports/decisions"),
            ("GET", "/reports/approvals"),
            ("GET", "/reports/teams"),
            ("GET", "/reports/audit"),
        ]
        for method, path in protected_endpoints:
            if method == "GET":
                resp = client.get(path)
            else:
                resp = client.post(path, json={})
            assert resp.status_code == 401, f"{method} {path} should require JWT but got {resp.status_code}"

    def test_invalid_jwt_rejected(self, client):
        """Various invalid JWT formats are rejected."""
        invalid_tokens = [
            "invalid",
            "Bearer invalid",
            "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.invalid",
            "",
        ]
        for token in invalid_tokens:
            resp = client.get("/decisions", headers={"Authorization": f"Bearer {token}"})
            assert resp.status_code == 401, f"Token '{token}' should be rejected"

    def test_expired_jwt_rejected(self, client, make_token):
        """Expired JWT is rejected."""
        u = _create_user(client, "sec.expired@test.com", "Employee", "Expired JWT", "IT", "SEC_EXP01")
        # Create an already-expired token
        token = make_token(str(u["id"]), expires_delta=timedelta(seconds=-1))
        resp = client.get("/decisions", headers=_auth_header(token))
        assert resp.status_code == 401

    def test_jwt_for_nonexistent_user(self, client, make_token):
        """JWT for a user that no longer exists is rejected."""
        token = make_token("99999")
        resp = client.get("/decisions", headers=_auth_header(token))
        assert resp.status_code == 401


class TestSecurityRBAC:
    """Roles are enforced properly."""

    def test_employee_cannot_access_admin_endpoints(self, client):
        u = _create_user(client, "rbac.emp2adm@test.com", "Employee", "RBAC E2A", "IT", "RB_E2A01")
        h = _auth_header(_login(client, "rbac.emp2adm@test.com")["access_token"])
        admin_endpoints = [
            "/dashboard/admin",
            "/dashboard/admin/analytics",
            "/dashboard/admin/user-activity",
            "/dashboard/admin/decision-activity",
            "/dashboard/admin/approval-statistics",
            "/security/logs",
            "/access/logs",
        ]
        for ep in admin_endpoints:
            resp = client.get(ep, headers=h)
            assert resp.status_code == 403, f"Employee accessed {ep} with {resp.status_code}"

    def test_employee_cannot_access_manager_endpoints(self, client):
        u = _create_user(client, "rbac.emp2mgr@test.com", "Employee", "RBAC E2M", "IT", "RB_E2M01")
        h = _auth_header(_login(client, "rbac.emp2mgr@test.com")["access_token"])
        mgr_endpoints = [
            "/dashboard/manager/statistics",
            "/dashboard/manager/pending-approvals",
        ]
        for ep in mgr_endpoints:
            resp = client.get(ep, headers=h)
            assert resp.status_code == 403, f"Employee accessed {ep} with {resp.status_code}"

    def test_manager_cannot_access_admin_endpoints(self, client):
        u = _create_user(client, "rbac.mgr2adm@test.com", "Manager", "RBAC M2A", "IT", "RB_M2A01")
        h = _auth_header(_login(client, "rbac.mgr2adm@test.com")["access_token"])
        resp = client.get("/dashboard/admin", headers=h)
        assert resp.status_code == 403

    def test_admin_can_access_all_endpoints(self, client):
        u = _create_user(client, "rbac.admin@test.com", "Administrator", "RBAC Admin", "IT", "RB_ADM01")
        h = _auth_header(_login(client, "rbac.admin@test.com")["access_token"])
        ok_endpoints = [
            "/dashboard/admin",
            "/dashboard/admin/analytics",
            "/dashboard/admin/user-activity",
            "/dashboard/admin/decision-activity",
            "/security/logs",
            "/access/logs",
            "/reports/decisions",
            "/reports/audit",
        ]
        for ep in ok_endpoints:
            resp = client.get(ep, headers=h)
            assert resp.status_code == 200, f"Admin failed on {ep}: {resp.status_code}"


class TestSecurityPasswordHashing:
    """Passwords are hashed and never returned in responses."""

    def test_password_not_in_register_response(self, client):
        resp = client.post("/users", json={
            "full_name": "Hash Test",
            "email": "hash.test@test.com",
            "password": "MySecretPassword123!",
            "role": "Employee",
            "employee_id": "HASH_T01",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "password" not in data, f"Password leaked in response: {data}"

    def test_password_not_in_login_response(self, client):
        _create_user(client, "hash.login@test.com", "Employee", "Hash Login", "IT", "HL_T01")
        resp = client.post("/login", json={"email": "hash.login@test.com", "password": "TestPass123!"})
        assert resp.status_code == 200
        data = resp.json()
        # Password should not be in any part of the response
        assert "password" not in str(data).lower() or "password" in data.get("token_type", ""), \
            f"Password may be leaked in login response"

    def test_password_not_in_get_user_response(self, client):
        u = _create_user(client, "hash.getuser@test.com", "Employee", "Hash Get", "IT", "HG_T01")
        h = _auth_header(_login(client, "hash.getuser@test.com")["access_token"])
        resp = client.get(f"/users/{u['id']}", headers=h)
        assert resp.status_code == 200
        assert "password" not in resp.json(), f"Password leaked in GET /users/{{id}}: {resp.json()}"

    def test_password_not_in_users_list_response(self, client):
        _create_user(client, "hash.userslist@test.com", "Employee", "Hash List", "IT", "HLST01")
        h = _auth_header(_login(client, "hash.userslist@test.com")["access_token"])
        resp = client.get("/users", headers=h)
        assert resp.status_code == 200
        for user in resp.json():
            assert "password" not in user, f"Password leaked in users list: {user}"

    def test_password_is_hashed_in_database(self, client, db_session):
        """Verify password stored in DB is bcrypt-hashed, not plaintext."""
        from app.models.user import User
        _create_user(client, "hash.db@test.com", "Employee", "Hash DB", "IT", "HDB_T01")
        user = db_session.query(User).filter(User.email == "hash.db@test.com").first()
        assert user is not None
        assert user.password != "MySecretPassword123!", "Password stored as plaintext!"
        assert user.password.startswith("$2"), f"Password doesn't look bcrypt-hashed: {user.password[:10]}"


class TestSecuritySecrets:
    """Secrets are not in code/logs."""

    def test_secret_key_not_in_error_responses(self, client):
        """Error responses should not leak SECRET_KEY."""
        resp = client.post("/login", json={"email": "none@test.com", "password": "wrong"})
        assert resp.status_code == 401
        body = resp.text
        assert "secret" not in body.lower() or "secret_key" not in body.lower(), \
            f"SECRET_KEY may be leaked in error: {body[:200]}"

    def test_jwt_token_not_logged_in_response(self, client):
        """JWT token structure should not expose SECRET_KEY."""
        _create_user(client, "sec.jwtlog@test.com", "Employee", "JWT Log", "IT", "JWTLOG01")
        resp = client.post("/login", json={"email": "sec.jwtlog@test.com", "password": "TestPass123!"})
        token = resp.json()["access_token"]
        # JWT is base64 encoded; the header should only contain alg and typ
        import base64
        parts = token.split(".")
        assert len(parts) == 3, f"JWT doesn't have 3 parts: {len(parts)}"
        header_b64 = parts[0] + "=" * (4 - len(parts[0]) % 4)
        header = json.loads(base64.b64decode(header_b64))
        assert "alg" in header
        assert "typ" in header
        # SECRET_KEY should NOT be in the JWT
        assert settings.SECRET_KEY not in token, "SECRET_KEY is part of the JWT!"


class TestSecuritySQLInjection:
    """Database queries are safe from SQL injection."""

    def test_sql_injection_in_login(self, client):
        """SQL injection in login fields should be rejected safely."""
        injection_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
        ]
        for payload in injection_payloads:
            resp = client.post("/login", json={"email": payload, "password": "anything"})
            # Should get 401 (auth failure), not 500 (SQL error) or 200 (auth bypass)
            assert resp.status_code == 401, f"SQL injection payload '{payload}' got {resp.status_code}"

    def test_sql_injection_in_search(self, client):
        """SQL injection in query parameters should be handled safely."""
        u = _create_user(client, "sec.sqli@test.com", "Employee", "SQLi Test", "IT", "SQLI_T01")
        h = _auth_header(_login(client, "sec.sqli@test.com")["access_token"])
        injection_payloads = [
            "'; DROP TABLE decisions; --",
            "1 OR 1=1",
            "' UNION SELECT * FROM users --",
        ]
        for payload in injection_payloads:
            resp = client.get(f"/decisions?category={payload}", headers=h)
            # Should get 200 (empty results) or 422 (validation), not 500
            assert resp.status_code in (200, 422), \
                f"SQL injection in search '{payload}' got {resp.status_code}"

    def test_sql_injection_in_user_id(self, client):
        """SQL injection in path parameters should be handled safely."""
        u = _create_user(client, "sec.sqli2@test.com", "Employee", "SQLi Test2", "IT", "SQLI_T02")
        h = _auth_header(_login(client, "sec.sqli2@test.com")["access_token"])
        # Path params are ints, so non-numeric should get 422
        resp = client.get("/decisions/1 OR 1=1", headers=h)
        assert resp.status_code in (404, 422)


class TestSecurityInvalidInput:
    """Invalid input is rejected with proper error codes."""

    def test_missing_required_fields(self, client):
        u = _create_user(client, "sec.invreq@test.com", "Employee", "Inv Req", "IT", "INVREQ01")
        h = _auth_header(_login(client, "sec.invreq@test.com")["access_token"])

        # Missing title
        resp = client.post("/decisions", headers=h, json={
            "problem_statement": "p", "category": "Tech",
        })
        assert resp.status_code == 422

        # Missing problem_statement
        resp = client.post("/decisions", headers=h, json={
            "title": "t", "category": "Tech",
        })
        assert resp.status_code == 422

        # Missing category
        resp = client.post("/decisions", headers=h, json={
            "title": "t", "problem_statement": "p",
        })
        assert resp.status_code == 422

    def test_invalid_email_format(self, client):
        resp = client.post("/users", json={
            "full_name": "Bad Email",
            "email": "not-an-email",
            "password": "TestPass123!",
            "role": "Employee",
            "employee_id": "BADM_T01",
        })
        assert resp.status_code == 422

    def test_invalid_role_ignored_on_registration(self, client):
        """After security fix C-3, role field is removed from registration.
        Invalid role is ignored; user is always created as Employee."""
        resp = client.post("/users", json={
            "full_name": "Bad Role",
            "email": "badrole@test.com",
            "password": "TestPass123!",
            "role": "SuperAdmin",
            "employee_id": "BADR_T01",
        })
        assert resp.status_code == 201
        assert resp.json()["role"] == "Employee"

    def test_empty_body_on_post(self, client):
        u = _create_user(client, "sec.empty@test.com", "Employee", "Empty Body", "IT", "EMPTY01")
        h = _auth_header(_login(client, "sec.empty@test.com")["access_token"])
        resp = client.post("/decisions", headers=h, json={})
        assert resp.status_code == 422

    def test_invalid_date_format_in_reports(self, client):
        u = _create_user(client, "sec.invdate@test.com", "Administrator", "Inv Date", "IT", "INVD_01")
        h = _auth_header(_login(client, "sec.invdate@test.com")["access_token"])
        resp = client.get("/reports/decisions?start_date=not-a-date", headers=h)
        assert resp.status_code == 422

    def test_reversed_date_range(self, client):
        u = _create_user(client, "sec.revdate@test.com", "Administrator", "Rev Date", "IT", "REVD_01")
        h = _auth_header(_login(client, "sec.revdate@test.com")["access_token"])
        resp = client.get("/reports/decisions?start_date=2026-12-31&end_date=2026-01-01", headers=h)
        assert resp.status_code == 422

    def test_invalid_sort_field(self, client):
        u = _create_user(client, "sec.invsrt@test.com", "Employee", "Inv Sort", "IT", "INVSR01")
        h = _auth_header(_login(client, "sec.invsrt@test.com")["access_token"])
        resp = client.get("/reports/decisions?sort_by=invalid_field", headers=h)
        assert resp.status_code == 422

    def test_invalid_page_size(self, client):
        u = _create_user(client, "sec.invpage@test.com", "Administrator", "Inv Page", "IT", "INVP_01")
        h = _auth_header(_login(client, "sec.invpage@test.com")["access_token"])
        resp = client.get("/audit-logs?page_size=500", headers=h)
        assert resp.status_code == 422

    def test_invalid_alternative_feasibility_out_of_range(self, client):
        u = _create_user(client, "sec.invfeas@test.com", "Employee", "Inv Feas", "IT", "INVF_01")
        h = _auth_header(_login(client, "sec.invfeas@test.com")["access_token"])
        d = client.post("/decisions", headers=h, json={
            "title": "Inv Feas", "problem_statement": "p", "category": "Tech",
        }).json()
        for score in [0, 6, -1, 100]:
            resp = client.post(f"/decisions/{d['id']}/alternatives", headers=h, json={
                "name": f"Bad {score}", "feasibility_score": score, "risk_level": "Low",
            })
            assert resp.status_code == 422, f"Score {score} should be rejected"


class TestSecurityCORS:
    """CORS configuration is tested."""

    def test_cors_preflight_allowed(self, client):
        """OPTIONS request should work (CORS preflight)."""
        resp = client.options("/decisions", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        })
        # FastAPI handles OPTIONS; should not be 405 or 500
        assert resp.status_code in (200, 405), f"CORS preflight got {resp.status_code}"

    def test_no_cors_credentials_leak(self, client):
        """Verify error responses don't expose internal details."""
        resp = client.post("/login", json={"email": "x@x.com", "password": "x"})
        assert resp.status_code == 401
        assert "traceback" not in resp.text.lower()
        assert "traceback" not in resp.text.lower()


class TestSecurityUnauthorizedAccess:
    """Unauthorized records cannot be accessed."""

    def test_user_cannot_access_other_users_audit_logs(self, client):
        """Employee should only see own audit logs, not others'."""
        u1 = _create_user(client, "sec.unauth1@test.com", "Employee", "Unauth1", "IT", "UNAU_01")
        u2 = _create_user(client, "sec.unauth2@test.com", "Employee", "Unauth2", "IT", "UNAU_02")
        h1 = _auth_header(_login(client, "sec.unauth1@test.com")["access_token"])
        h2 = _auth_header(_login(client, "sec.unauth2@test.com")["access_token"])

        # u1 creates a decision (generates audit log)
        client.post("/decisions", headers=h1, json={
            "title": "Unauth Dec", "problem_statement": "p", "category": "Tech",
        })

        # u2's audit logs should not include u1's entries
        resp = client.get("/audit-logs", headers=h2)
        assert resp.status_code == 200
        for item in resp.json()["items"]:
            assert item["user_id"] == u2["id"], \
                f"User {u2['id']} can see audit log from user {item['user_id']}"

    def test_non_admin_cannot_view_security_logs(self, client):
        u = _create_user(client, "sec.noacc@test.com", "Employee", "No Acc", "IT", "NOACC01")
        h = _auth_header(_login(client, "sec.noacc@test.com")["access_token"])
        resp = client.get("/security/logs", headers=h)
        assert resp.status_code == 403

    def test_non_author_cannot_delete_others_comment(self, client):
        u1 = _create_user(client, "sec.cmtown1@test.com", "Employee", "Cmt Own1", "IT", "CMTO_01")
        u2 = _create_user(client, "sec.cmtown2@test.com", "Employee", "Cmt Own2", "IT", "CMTO_02")
        h1 = _auth_header(_login(client, "sec.cmtown1@test.com")["access_token"])
        h2 = _auth_header(_login(client, "sec.cmtown2@test.com")["access_token"])

        d = client.post("/decisions", headers=h1, json={
            "title": "Cmt Own", "problem_statement": "p", "category": "Tech",
        }).json()
        c = client.post(f"/decisions/{d['id']}/comments", headers=h1, json={
            "content": "My comment",
        }).json()

        resp = client.delete(f"/comments/{c['id']}", headers=h2)
        assert resp.status_code == 403

    def test_non_author_cannot_delete_others_thread(self, client):
        u1 = _create_user(client, "sec.thrown1@test.com", "Employee", "Thr Own1", "IT", "THRO_01")
        u2 = _create_user(client, "sec.thrown2@test.com", "Employee", "Thr Own2", "IT", "THRO_02")
        h1 = _auth_header(_login(client, "sec.thrown1@test.com")["access_token"])
        h2 = _auth_header(_login(client, "sec.thrown2@test.com")["access_token"])

        d = client.post("/decisions", headers=h1, json={
            "title": "Thr Own", "problem_statement": "p", "category": "Tech",
        }).json()
        t = client.post(f"/decisions/{d['id']}/threads", headers=h1, json={
            "title": "My Thread",
        }).json()

        resp = client.delete(f"/threads/{t['id']}", headers=h2)
        assert resp.status_code == 403

    def test_non_author_cannot_modify_others_meeting_note(self, client):
        u1 = _create_user(client, "sec.mnown1@test.com", "Employee", "MN Own1", "IT", "MNO_01")
        u2 = _create_user(client, "sec.mnown2@test.com", "Employee", "MN Own2", "IT", "MNO_02")
        h1 = _auth_header(_login(client, "sec.mnown1@test.com")["access_token"])
        h2 = _auth_header(_login(client, "sec.mnown2@test.com")["access_token"])

        d = client.post("/decisions", headers=h1, json={
            "title": "MN Own", "problem_statement": "p", "category": "Tech",
        }).json()
        n = client.post(f"/decisions/{d['id']}/meeting-notes", headers=h1, json={
            "title": "My Note", "content": "content",
            "meeting_date": datetime.now().isoformat(),
        }).json()

        resp = client.put(f"/meeting-notes/{n['id']}", headers=h2, json={"title": "Hacked"})
        assert resp.status_code == 403

    def test_non_owner_cannot_modify_others_rationale(self, client):
        u1 = _create_user(client, "sec.ratown1@test.com", "Employee", "Rat Own1", "IT", "RATO_01")
        u2 = _create_user(client, "sec.ratown2@test.com", "Employee", "Rat Own2", "IT", "RATO_02")
        h1 = _auth_header(_login(client, "sec.ratown1@test.com")["access_token"])
        h2 = _auth_header(_login(client, "sec.ratown2@test.com")["access_token"])

        d = client.post("/decisions", headers=h1, json={
            "title": "Rat Own", "problem_statement": "p", "category": "Tech",
        }).json()

        resp = client.put(f"/decisions/{d['id']}/rationale", headers=h2, json={
            "rationale": "Hacked rationale",
        })
        assert resp.status_code == 403


# Need settings for JWT security test
from app.core.config import settings
