"""
Phase 2 — Workflow, Security & Validation

Tests the complete decision lifecycle with separate users for:
  Employee, Reviewer, Manager, Administrator

Covers: Authentication, Permissions, Decision states, Validation, Error handling.
"""

from datetime import timedelta

import pytest

from app.core.security import create_access_token, hash_password, verify_token
from app.models.alternative import Alternative
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.discussion_thread import DiscussionThread
from app.models.enums import DecisionStatus, RiskLevel, UserRole
from app.models.meeting_note import MeetingNote
from app.models.user import User


# ---------------------------------------------------------------------------
# Fixtures — four role-specific users
# ---------------------------------------------------------------------------

def _make_user(db_session, email, employee_id, role=UserRole.EMPLOYEE):
    user = User(
        full_name=f"{role.value} User",
        email=email,
        role=role,
        password=hash_password("password123"),
        employee_id=employee_id,
        department="Engineering",
        designation="Senior",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def employee(db_session):
    return _make_user(db_session, "employee@phase2.com", "EMP_P2_E", UserRole.EMPLOYEE)


@pytest.fixture()
def reviewer(db_session):
    return _make_user(db_session, "reviewer@phase2.com", "EMP_P2_R", UserRole.REVIEWER)


@pytest.fixture()
def manager(db_session):
    return _make_user(db_session, "manager@phase2.com", "EMP_P2_M", UserRole.MANAGER)


@pytest.fixture()
def admin(db_session):
    return _make_user(db_session, "admin@phase2.com", "EMP_P2_A", UserRole.ADMINISTRATOR)


def _headers(user, make_token):
    token = make_token(str(user.id))
    return {"Authorization": f"Bearer {token}"}


def _create_decision(db_session, user, title="Phase2 Decision", status="Draft"):
    d = Decision(
        title=title,
        problem_statement="Problem",
        category="Technology",
        status=status,
        created_by=user.id,
    )
    db_session.add(d)
    db_session.commit()
    db_session.refresh(d)
    return d


def _create_alternative(db_session, decision, name="Alt A"):
    a = Alternative(
        decision_id=decision.id,
        name=name,
        description="desc",
        pros="pros",
        cons="cons",
        estimated_cost=1000,
        feasibility_score=3,
        risk_level="Medium",
    )
    db_session.add(a)
    db_session.commit()
    db_session.refresh(a)
    return a


def _create_comment(db_session, decision, user, content="Test comment"):
    c = Comment(
        decision_id=decision.id,
        user_id=user.id,
        content=content,
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return c


def _create_thread(db_session, decision, user, title="Thread"):
    t = DiscussionThread(
        decision_id=decision.id,
        created_by=user.id,
        title=title,
    )
    db_session.add(t)
    db_session.commit()
    db_session.refresh(t)
    return t


def _create_meeting_note(db_session, decision, user, title="Note"):
    from datetime import datetime
    n = MeetingNote(
        decision_id=decision.id,
        created_by=user.id,
        title=title,
        content="content",
        meeting_date=datetime(2026, 1, 1),
    )
    db_session.add(n)
    db_session.commit()
    db_session.refresh(n)
    return n


# ===================================================================
# 1. AUTHENTICATION
# ===================================================================

class TestAuthentication:
    """Test valid login, invalid credentials, missing fields, missing/invalid/expired JWT."""

    def test_valid_login(self, client, db_session):
        _make_user(db_session, "login_ok@auth.com", "EMP_A1")
        resp = client.post("/login", json={"email": "login_ok@auth.com", "password": "password123"})
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        assert body["user"]["email"] == "login_ok@auth.com"

    def test_invalid_password(self, client, db_session):
        _make_user(db_session, "login_badpw@auth.com", "EMP_A2")
        resp = client.post("/login", json={"email": "login_badpw@auth.com", "password": "wrong"})
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Incorrect email or password"

    def test_unknown_email(self, client, db_session):
        _make_user(db_session, "login_real@auth.com", "EMP_A3")
        resp = client.post("/login", json={"email": "nobody@auth.com", "password": "password123"})
        assert resp.status_code == 401

    def test_missing_email_field(self, client, db_session):
        resp = client.post("/login", json={"password": "password123"})
        assert resp.status_code == 422

    def test_missing_password_field(self, client, db_session):
        resp = client.post("/login", json={"email": "x@auth.com"})
        assert resp.status_code == 422

    def test_empty_body(self, client, db_session):
        resp = client.post("/login", json={})
        assert resp.status_code == 422

    def test_missing_jwt_on_protected_endpoint(self, client, db_session):
        resp = client.get("/decisions")
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Not authenticated"

    def test_invalid_jwt_format(self, client, db_session):
        resp = client.get("/decisions", headers={"Authorization": "Bearer not.a.valid.jwt"})
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid or expired token"

    def test_invalid_jwt_random_string(self, client, db_session):
        resp = client.get("/decisions", headers={"Authorization": "Bearer completelygarbage"})
        assert resp.status_code == 401

    def test_expired_jwt(self, client, db_session, make_token):
        user = _make_user(db_session, "expired_jwt@auth.com", "EMP_A4")
        expired_token = create_access_token(
            {"sub": str(user.id)},
            expires_delta=timedelta(seconds=-1),
        )
        resp = client.get("/decisions", headers={"Authorization": f"Bearer {expired_token}"})
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid or expired token"

    def test_jwt_with_nonexistent_user(self, client, db_session):
        token = create_access_token({"sub": "99999999"})
        resp = client.get("/decisions", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401
        assert resp.json()["detail"] == "User not found"

    def test_jwt_with_no_sub_claim(self, client, db_session):
        token = create_access_token({"foo": "bar"})
        resp = client.get("/decisions", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid or expired token"

    def test_malformed_bearer_header(self, client, db_session):
        resp = client.get("/decisions", headers={"Authorization": "Token abc123"})
        assert resp.status_code == 401

    def test_logout_requires_auth(self, client, db_session):
        resp = client.post("/login/logout")
        assert resp.status_code == 401

    def test_logout_with_valid_token(self, client, db_session, make_token):
        user = _make_user(db_session, "logout_ok@auth.com", "EMP_A5")
        resp = client.post("/login/logout", headers=_headers(user, make_token))
        assert resp.status_code == 200
        assert resp.json()["message"] == "Logged out successfully"


# ===================================================================
# 2. PERMISSIONS (RBAC)
# ===================================================================

class TestPermissions:
    """Verify each role can only perform its allowed actions."""

    # --- Employee permissions ---
    def test_employee_can_create_decision(self, client, employee, make_token):
        resp = client.post("/decisions", json={
            "title": "Emp Decision", "problem_statement": "p", "category": "c",
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 201
        assert resp.json()["created_by"] == employee.id

    def test_employee_can_view_own_decisions(self, client, db_session, employee, make_token):
        _create_decision(db_session, employee)
        resp = client.get("/decisions", headers=_headers(employee, make_token))
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_employee_can_update_own_decision(self, client, db_session, employee, make_token):
        d = _create_decision(db_session, employee)
        resp = client.put(f"/decisions/{d.id}", json={"title": "Updated"}, headers=_headers(employee, make_token))
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated"

    def test_employee_can_create_alternative(self, client, db_session, employee, make_token):
        d = _create_decision(db_session, employee)
        resp = client.post(f"/decisions/{d.id}/alternatives", json={
            "name": "Alt", "feasibility_score": 3, "risk_level": "Low",
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 201

    def test_employee_can_create_comment(self, client, db_session, employee, make_token):
        d = _create_decision(db_session, employee)
        resp = client.post(f"/decisions/{d.id}/comments", json={
            "content": "My comment",
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 201

    def test_employee_can_create_thread(self, client, db_session, employee, make_token):
        d = _create_decision(db_session, employee)
        resp = client.post(f"/decisions/{d.id}/threads", json={
            "title": "My thread",
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 201

    def test_employee_can_view_employee_dashboard(self, client, employee, make_token):
        resp = client.get("/dashboard/employee", headers=_headers(employee, make_token))
        assert resp.status_code == 200
        assert "total_decisions" in resp.json()

    def test_employee_cannot_access_manager_dashboard(self, client, employee, make_token):
        resp = client.get("/dashboard/manager/statistics", headers=_headers(employee, make_token))
        assert resp.status_code == 403

    def test_employee_cannot_access_admin_dashboard(self, client, employee, make_token):
        resp = client.get("/dashboard/admin", headers=_headers(employee, make_token))
        assert resp.status_code == 403

    def test_employee_cannot_view_security_logs(self, client, employee, make_token):
        resp = client.get("/security/logs", headers=_headers(employee, make_token))
        assert resp.status_code == 403

    def test_employee_cannot_view_access_logs(self, client, employee, make_token):
        resp = client.get("/access/logs", headers=_headers(employee, make_token))
        assert resp.status_code == 403

    def test_employee_can_view_activities_own_only(self, client, db_session, employee, make_token):
        resp = client.get("/activities", headers=_headers(employee, make_token))
        assert resp.status_code == 200

    # --- Reviewer permissions ---
    def test_reviewer_can_create_decision(self, client, reviewer, make_token):
        resp = client.post("/decisions", json={
            "title": "Rev Decision", "problem_statement": "p", "category": "c",
        }, headers=_headers(reviewer, make_token))
        assert resp.status_code == 201

    def test_reviewer_can_view_dashboard(self, client, reviewer, make_token):
        resp = client.get("/dashboard/employee", headers=_headers(reviewer, make_token))
        assert resp.status_code == 200

    def test_reviewer_cannot_access_manager_dashboard(self, client, reviewer, make_token):
        resp = client.get("/dashboard/manager/statistics", headers=_headers(reviewer, make_token))
        assert resp.status_code == 403

    def test_reviewer_cannot_view_security_logs(self, client, reviewer, make_token):
        resp = client.get("/security/logs", headers=_headers(reviewer, make_token))
        assert resp.status_code == 403

    # --- Manager permissions ---
    def test_manager_can_access_manager_dashboard(self, client, manager, make_token):
        resp = client.get("/dashboard/manager/statistics", headers=_headers(manager, make_token))
        assert resp.status_code == 200

    def test_manager_cannot_access_admin_dashboard(self, client, manager, make_token):
        resp = client.get("/dashboard/admin", headers=_headers(manager, make_token))
        assert resp.status_code == 403

    def test_manager_can_view_security_logs(self, client, manager, make_token):
        resp = client.get("/security/logs", headers=_headers(manager, make_token))
        assert resp.status_code == 200

    def test_manager_can_view_access_logs(self, client, manager, make_token):
        resp = client.get("/access/logs", headers=_headers(manager, make_token))
        assert resp.status_code == 200

    def test_manager_can_view_audit_logs(self, client, manager, make_token):
        resp = client.get("/audit/logs", headers=_headers(manager, make_token))
        assert resp.status_code == 200

    # --- Administrator permissions ---
    def test_admin_can_access_admin_dashboard(self, client, admin, make_token):
        resp = client.get("/dashboard/admin", headers=_headers(admin, make_token))
        assert resp.status_code == 200
        assert "total_users" in resp.json()

    def test_admin_can_access_manager_dashboard(self, client, admin, make_token):
        resp = client.get("/dashboard/manager/statistics", headers=_headers(admin, make_token))
        assert resp.status_code == 200

    def test_admin_can_view_security_logs(self, client, admin, make_token):
        resp = client.get("/security/logs", headers=_headers(admin, make_token))
        assert resp.status_code == 200

    def test_admin_can_view_access_logs(self, client, admin, make_token):
        resp = client.get("/access/logs", headers=_headers(admin, make_token))
        assert resp.status_code == 200

    def test_admin_can_view_all_users(self, client, admin, make_token):
        resp = client.get("/users", headers=_headers(admin, make_token))
        assert resp.status_code == 200

    def test_admin_can_update_others_rationale(self, client, db_session, employee, admin, make_token):
        d = _create_decision(db_session, employee)
        resp = client.put(f"/decisions/{d.id}/rationale", json={
            "rationale": "Admin override rationale",
        }, headers=_headers(admin, make_token))
        assert resp.status_code == 200

    def test_admin_can_update_other_users_comment(self, client, db_session, employee, admin, make_token):
        d = _create_decision(db_session, employee)
        c = _create_comment(db_session, d, employee)
        resp = client.put(f"/comments/{c.id}", json={
            "content": "Admin edited comment",
        }, headers=_headers(admin, make_token))
        assert resp.status_code == 200

    def test_admin_can_delete_other_users_thread(self, client, db_session, employee, admin, make_token):
        d = _create_decision(db_session, employee)
        t = _create_thread(db_session, d, employee)
        resp = client.delete(f"/threads/{t.id}", headers=_headers(admin, make_token))
        assert resp.status_code == 200

    def test_admin_can_view_reports(self, client, admin, make_token):
        resp = client.get("/reports/decisions", headers=_headers(admin, make_token))
        assert resp.status_code == 200

    # --- Cross-role authorization failures ---
    def test_employee_cannot_update_other_comment(self, client, db_session, employee, reviewer, make_token):
        d = _create_decision(db_session, employee)
        c = _create_comment(db_session, d, reviewer)
        resp = client.put(f"/comments/{c.id}", json={
            "content": "Hacked",
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 403

    def test_employee_cannot_update_other_thread(self, client, db_session, employee, reviewer, make_token):
        d = _create_decision(db_session, employee)
        t = _create_thread(db_session, d, reviewer)
        resp = client.put(f"/threads/{t.id}", json={
            "title": "Hacked",
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 403

    def test_employee_cannot_delete_other_meeting_note(self, client, db_session, employee, reviewer, make_token):
        d = _create_decision(db_session, employee)
        n = _create_meeting_note(db_session, d, reviewer)
        resp = client.delete(f"/meeting-notes/{n.id}", headers=_headers(employee, make_token))
        assert resp.status_code == 403

    def test_employee_cannot_update_other_rationale(self, client, db_session, employee, reviewer, make_token):
        d = _create_decision(db_session, employee)
        resp = client.put(f"/decisions/{d.id}/rationale", json={
            "rationale": "Stolen",
        }, headers=_headers(reviewer, make_token))
        assert resp.status_code == 403


# ===================================================================
# 3. DECISION STATES (Workflow)
# ===================================================================

class TestDecisionStates:
    """Test valid and invalid decision state transitions."""

    def test_draft_to_under_review(self, client, db_session, employee, make_token):
        d = _create_decision(db_session, employee, status="Draft")
        resp = client.patch(f"/decisions/{d.id}/status", json={
            "status": "Under Review",
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 200
        assert resp.json()["status"] == "Under Review"

    def test_under_review_to_approved(self, client, db_session, employee, make_token):
        d = _create_decision(db_session, employee, status="Under Review")
        resp = client.patch(f"/decisions/{d.id}/status", json={
            "status": "Approved",
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 200
        assert resp.json()["status"] == "Approved"

    def test_under_review_to_rejected(self, client, db_session, employee, make_token):
        d = _create_decision(db_session, employee, status="Under Review")
        resp = client.patch(f"/decisions/{d.id}/status", json={
            "status": "Rejected",
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 200
        assert resp.json()["status"] == "Rejected"

    def test_full_lifecycle_approved(self, client, db_session, employee, make_token):
        d = _create_decision(db_session, employee, status="Draft")
        h = _headers(employee, make_token)
        # Draft → Under Review
        r1 = client.patch(f"/decisions/{d.id}/status", json={"status": "Under Review"}, headers=h)
        assert r1.status_code == 200
        # Under Review → Approved
        r2 = client.patch(f"/decisions/{d.id}/status", json={"status": "Approved"}, headers=h)
        assert r2.status_code == 200
        assert r2.json()["status"] == "Approved"

    def test_full_lifecycle_rejected(self, client, db_session, employee, make_token):
        d = _create_decision(db_session, employee, status="Draft")
        h = _headers(employee, make_token)
        client.patch(f"/decisions/{d.id}/status", json={"status": "Under Review"}, headers=h)
        r = client.patch(f"/decisions/{d.id}/status", json={"status": "Rejected"}, headers=h)
        assert r.status_code == 200
        assert r.json()["status"] == "Rejected"

    def test_approved_to_archived(self, client, db_session, employee, make_token):
        d = _create_decision(db_session, employee, status="Approved")
        resp = client.patch(f"/decisions/{d.id}/status", json={
            "status": "Archived",
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 200
        assert resp.json()["status"] == "Archived"

    def test_rejected_to_archived(self, client, db_session, employee, make_token):
        d = _create_decision(db_session, employee, status="Rejected")
        resp = client.patch(f"/decisions/{d.id}/status", json={
            "status": "Archived",
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 200
        assert resp.json()["status"] == "Archived"

    def test_invalid_status_value_rejected(self, client, db_session, employee, make_token):
        d = _create_decision(db_session, employee)
        resp = client.patch(f"/decisions/{d.id}/status", json={
            "status": "InvalidStatus",
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 422

    def test_archived_to_draft_allowed(self, client, db_session, employee, make_token):
        """Current implementation has NO transition validation — Archived → Draft is allowed.
        This tests the current (permissive) behavior."""
        d = _create_decision(db_session, employee, status="Archived")
        resp = client.patch(f"/decisions/{d.id}/status", json={
            "status": "Draft",
        }, headers=_headers(employee, make_token))
        # Current code allows any status transition
        assert resp.status_code == 200
        assert resp.json()["status"] == "Draft"

    def test_status_change_creates_version(self, client, employee, make_token):
        h = _headers(employee, make_token)
        # Create decision through API so version 1 is auto-created
        r = client.post("/decisions", json={
            "title": "Version Test", "problem_statement": "p", "category": "c",
        }, headers=h)
        d_id = r.json()["id"]

        resp = client.patch(f"/decisions/{d_id}/status", json={
            "status": "Under Review",
        }, headers=h)
        assert resp.status_code == 200

        versions = client.get(f"/decisions/{d_id}/versions", headers=h)
        assert versions.status_code == 200
        v_list = versions.json()["versions"]
        assert len(v_list) >= 2  # version 1 from creation + version from status change

    def test_status_change_decision_not_found(self, client, employee, make_token):
        resp = client.patch("/decisions/99999999/status", json={
            "status": "Approved",
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 404

    def test_status_change_requires_auth(self, client, db_session, employee):
        d = _create_decision(db_session, employee)
        resp = client.patch(f"/decisions/{d.id}/status", json={"status": "Approved"})
        assert resp.status_code == 401


# ===================================================================
# 4. VALIDATION
# ===================================================================

class TestValidation:
    """Test invalid required fields, email, IDs, status, feasibility score, risk level."""

    # --- User validation ---
    def test_create_user_missing_full_name(self, client, db_session):
        resp = client.post("/users", json={
            "email": "v1@test.com", "password": "password1234", "employee_id": "V1",
        })
        assert resp.status_code == 422

    def test_create_user_missing_email(self, client, db_session):
        resp = client.post("/users", json={
            "full_name": "V", "password": "password1234", "employee_id": "V2",
        })
        assert resp.status_code == 422

    def test_create_user_invalid_email(self, client, db_session):
        resp = client.post("/users", json={
            "full_name": "V", "email": "not-an-email", "password": "password1234", "employee_id": "V3",
        })
        assert resp.status_code == 422

    def test_create_user_missing_password(self, client, db_session):
        resp = client.post("/users", json={
            "full_name": "V", "email": "v4@test.com", "employee_id": "V4",
        })
        assert resp.status_code == 422

    def test_create_user_missing_employee_id(self, client, db_session):
        resp = client.post("/users", json={
            "full_name": "V", "email": "v5@test.com", "password": "password1234",
        })
        assert resp.status_code == 422

    def test_create_user_invalid_role(self, client, db_session):
        """After security fix C-3, role field is not in registration schema.
        Invalid role field is ignored; user is created as Employee."""
        resp = client.post("/users", json={
            "full_name": "V", "email": "v6@test.com", "password": "password1234",
            "employee_id": "V6", "role": "SuperAdmin",
        })
        assert resp.status_code == 201
        assert resp.json()["role"] == "Employee"

    def test_create_user_duplicate_email(self, client, db_session):
        _make_user(db_session, "dup@test.com", "DUP1")
        resp = client.post("/users", json={
            "full_name": "Dup", "email": "dup@test.com", "password": "password1234",
            "employee_id": "DUP2",
        })
        assert resp.status_code == 400
        assert "Email already registered" in resp.json()["detail"]

    def test_create_user_duplicate_employee_id(self, client, db_session):
        _make_user(db_session, "dup2@test.com", "DUP_E1")
        resp = client.post("/users", json={
            "full_name": "Dup2", "email": "dup22@test.com", "password": "password1234",
            "employee_id": "DUP_E1",
        })
        assert resp.status_code == 400
        assert "Employee ID already registered" in resp.json()["detail"]

    # --- Decision validation ---
    def test_create_decision_missing_title(self, client, employee, make_token):
        resp = client.post("/decisions", json={
            "problem_statement": "p", "category": "c",
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 422

    def test_create_decision_missing_problem_statement(self, client, employee, make_token):
        resp = client.post("/decisions", json={
            "title": "T", "category": "c",
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 422

    def test_create_decision_missing_category(self, client, employee, make_token):
        resp = client.post("/decisions", json={
            "title": "T", "problem_statement": "p",
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 422

    def test_create_decision_empty_body(self, client, employee, make_token):
        resp = client.post("/decisions", json={}, headers=_headers(employee, make_token))
        assert resp.status_code == 422

    def test_patch_status_invalid_enum(self, client, db_session, employee, make_token):
        d = _create_decision(db_session, employee)
        resp = client.patch(f"/decisions/{d.id}/status", json={
            "status": "Done",
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 422

    # --- Alternative validation ---
    def test_create_alternative_missing_name(self, client, db_session, employee, make_token):
        d = _create_decision(db_session, employee)
        resp = client.post(f"/decisions/{d.id}/alternatives", json={
            "feasibility_score": 3, "risk_level": "Low",
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 422

    def test_create_alternative_invalid_feasibility_too_high(self, client, db_session, employee, make_token):
        d = _create_decision(db_session, employee)
        resp = client.post(f"/decisions/{d.id}/alternatives", json={
            "name": "Alt", "feasibility_score": 6,
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 422

    def test_create_alternative_invalid_feasibility_too_low(self, client, db_session, employee, make_token):
        d = _create_decision(db_session, employee)
        resp = client.post(f"/decisions/{d.id}/alternatives", json={
            "name": "Alt", "feasibility_score": 0,
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 422

    def test_create_alternative_invalid_risk_level(self, client, db_session, employee, make_token):
        d = _create_decision(db_session, employee)
        resp = client.post(f"/decisions/{d.id}/alternatives", json={
            "name": "Alt", "risk_level": "Extreme",
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 422

    def test_create_alternative_valid_risk_levels(self, client, db_session, employee, make_token):
        d = _create_decision(db_session, employee)
        h = _headers(employee, make_token)
        for level in ["Low", "Medium", "High", "Critical"]:
            resp = client.post(f"/decisions/{d.id}/alternatives", json={
                "name": f"Alt-{level}", "risk_level": level,
            }, headers=h)
            assert resp.status_code == 201, f"Expected 201 for risk_level={level}, got {resp.status_code}"

    def test_create_alternative_valid_feasibility_scores(self, client, db_session, employee, make_token):
        d = _create_decision(db_session, employee)
        h = _headers(employee, make_token)
        for score in [1, 2, 3, 4, 5]:
            resp = client.post(f"/decisions/{d.id}/alternatives", json={
                "name": f"Alt-s{score}", "feasibility_score": score,
            }, headers=h)
            assert resp.status_code == 201, f"Expected 201 for score={score}, got {resp.status_code}"

    # --- Comment validation ---
    def test_create_comment_missing_content(self, client, db_session, employee, make_token):
        d = _create_decision(db_session, employee)
        resp = client.post(f"/decisions/{d.id}/comments", json={},
                           headers=_headers(employee, make_token))
        assert resp.status_code == 422

    # --- Thread validation ---
    def test_create_thread_missing_title(self, client, db_session, employee, make_token):
        d = _create_decision(db_session, employee)
        resp = client.post(f"/decisions/{d.id}/threads", json={},
                           headers=_headers(employee, make_token))
        assert resp.status_code == 422

    # --- Meeting note validation ---
    def test_create_meeting_note_missing_fields(self, client, db_session, employee, make_token):
        d = _create_decision(db_session, employee)
        resp = client.post(f"/decisions/{d.id}/meeting-notes", json={},
                           headers=_headers(employee, make_token))
        assert resp.status_code == 422


# ===================================================================
# 5. ERROR HANDLING (404 Not Found)
# ===================================================================

class TestErrorHandling:
    """Test missing user, decision, alternative, comment → 404. No tracebacks."""

    def test_get_nonexistent_user(self, client, admin, make_token):
        resp = client.get("/users/99999999", headers=_headers(admin, make_token))
        assert resp.status_code == 404
        assert resp.json()["detail"] == "User not found"

    def test_update_nonexistent_user(self, client, admin, make_token):
        resp = client.put("/users/99999999", json={"full_name": "X"},
                          headers=_headers(admin, make_token))
        assert resp.status_code == 404

    def test_delete_nonexistent_user(self, client, admin, make_token):
        resp = client.delete("/users/99999999", headers=_headers(admin, make_token))
        assert resp.status_code == 404

    def test_get_nonexistent_decision(self, client, employee, make_token):
        resp = client.get("/decisions/99999999", headers=_headers(employee, make_token))
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Decision not found"

    def test_update_nonexistent_decision(self, client, employee, make_token):
        resp = client.put("/decisions/99999999", json={"title": "X"},
                          headers=_headers(employee, make_token))
        assert resp.status_code == 404

    def test_patch_status_nonexistent_decision(self, client, employee, make_token):
        resp = client.patch("/decisions/99999999/status", json={"status": "Approved"},
                            headers=_headers(employee, make_token))
        assert resp.status_code == 404

    def test_get_nonexistent_alternative(self, client, employee, make_token):
        resp = client.get("/alternatives/99999999", headers=_headers(employee, make_token))
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Alternative not found"

    def test_update_nonexistent_alternative(self, client, employee, make_token):
        resp = client.put("/alternatives/99999999", json={"name": "X"},
                          headers=_headers(employee, make_token))
        assert resp.status_code == 404

    def test_delete_nonexistent_alternative(self, client, employee, make_token):
        resp = client.delete("/alternatives/99999999", headers=_headers(employee, make_token))
        assert resp.status_code == 404

    def test_get_nonexistent_comment(self, client, employee, make_token):
        resp = client.get("/comments/99999999", headers=_headers(employee, make_token))
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Comment not found"

    def test_update_nonexistent_comment(self, client, employee, make_token):
        resp = client.put("/comments/99999999", json={"content": "X"},
                          headers=_headers(employee, make_token))
        assert resp.status_code == 404

    def test_delete_nonexistent_comment(self, client, employee, make_token):
        resp = client.delete("/comments/99999999", headers=_headers(employee, make_token))
        assert resp.status_code == 404

    def test_get_nonexistent_thread(self, client, employee, make_token):
        resp = client.get("/threads/99999999", headers=_headers(employee, make_token))
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Thread not found"

    def test_update_nonexistent_thread(self, client, employee, make_token):
        resp = client.put("/threads/99999999", json={"title": "X"},
                          headers=_headers(employee, make_token))
        assert resp.status_code == 404

    def test_delete_nonexistent_thread(self, client, employee, make_token):
        resp = client.delete("/threads/99999999", headers=_headers(employee, make_token))
        assert resp.status_code == 404

    def test_get_nonexistent_meeting_note(self, client, employee, make_token):
        resp = client.get("/meeting-notes/99999999", headers=_headers(employee, make_token))
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Meeting note not found"

    def test_update_nonexistent_meeting_note(self, client, employee, make_token):
        resp = client.put("/meeting-notes/99999999", json={"title": "X"},
                          headers=_headers(employee, make_token))
        assert resp.status_code == 404

    def test_delete_nonexistent_meeting_note(self, client, employee, make_token):
        resp = client.delete("/meeting-notes/99999999", headers=_headers(employee, make_token))
        assert resp.status_code == 404

    def test_alternatives_on_nonexistent_decision(self, client, employee, make_token):
        resp = client.post("/decisions/99999999/alternatives", json={
            "name": "Alt",
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 404

    def test_comments_on_nonexistent_decision(self, client, employee, make_token):
        resp = client.post("/decisions/99999999/comments", json={
            "content": "Comment",
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 404

    def test_threads_on_nonexistent_decision(self, client, employee, make_token):
        resp = client.post("/decisions/99999999/threads", json={
            "title": "Thread",
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 404

    def test_meeting_notes_on_nonexistent_decision(self, client, employee, make_token):
        resp = client.post("/decisions/99999999/meeting-notes", json={
            "title": "Note", "content": "Content", "meeting_date": "2026-01-01T00:00:00",
        }, headers=_headers(employee, make_token))
        assert resp.status_code == 404

    def test_versions_on_nonexistent_decision(self, client, employee, make_token):
        resp = client.get("/decisions/99999999/versions", headers=_headers(employee, make_token))
        assert resp.status_code == 404

    def test_history_on_nonexistent_decision(self, client, employee, make_token):
        resp = client.get("/decisions/99999999/history", headers=_headers(employee, make_token))
        assert resp.status_code == 404

    def test_nonexistent_security_log(self, client, manager, make_token):
        resp = client.get("/security/logs/99999999", headers=_headers(manager, make_token))
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Security log not found"

    def test_nonexistent_access_log(self, client, manager, make_token):
        resp = client.get("/access/logs/99999999", headers=_headers(manager, make_token))
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Access log not found"

    def test_nonexistent_audit_log(self, client, admin, make_token):
        resp = client.get("/audit/logs/99999999", headers=_headers(admin, make_token))
        assert resp.status_code == 404

    def test_error_responses_are_json_not_traceback(self, client, employee, make_token):
        """Verify error responses contain a 'detail' key, not a Python traceback."""
        resp = client.get("/decisions/99999999", headers=_headers(employee, make_token))
        body = resp.json()
        assert "detail" in body
        assert "traceback" not in body
        assert "Traceback" not in str(body)


# ===================================================================
# 6. DATABASE CONFLICT / INTEGRITY ERRORS
# ===================================================================

class TestDatabaseConflictHandling:
    """Verify database conflicts return proper errors, not tracebacks."""

    def test_duplicate_email_returns_400(self, client, db_session):
        _make_user(db_session, "conflict@test.com", "CONF1")
        resp = client.post("/users", json={
            "full_name": "Conflict", "email": "conflict@test.com",
            "password": "password1234", "employee_id": "CONF2",
        })
        assert resp.status_code == 400
        assert "detail" in resp.json()

    def test_duplicate_employee_id_returns_400(self, client, db_session):
        _make_user(db_session, "conflict2@test.com", "CONF_E1")
        resp = client.post("/users", json={
            "full_name": "Conflict2", "email": "conflict22@test.com",
            "password": "password1234", "employee_id": "CONF_E1",
        })
        assert resp.status_code == 400

    def test_invalid_date_format_returns_422(self, client, admin, make_token):
        resp = client.get("/reports/decisions?start_date=not-a-date",
                          headers=_headers(admin, make_token))
        assert resp.status_code == 422

    def test_reversed_date_range_returns_422(self, client, admin, make_token):
        resp = client.get("/reports/decisions?start_date=2026-12-31&end_date=2026-01-01",
                          headers=_headers(admin, make_token))
        assert resp.status_code == 422

    def test_invalid_sort_field_returns_422(self, client, admin, make_token):
        resp = client.get("/reports/decisions?sort_by=nonexistent_field",
                          headers=_headers(admin, make_token))
        assert resp.status_code == 422

    def test_invalid_sort_order_returns_422(self, client, admin, make_token):
        resp = client.get("/reports/decisions?sort_order=random",
                          headers=_headers(admin, make_token))
        assert resp.status_code == 422

    def test_invalid_page_size_returns_422(self, client, admin, make_token):
        resp = client.get("/reports/decisions?page_size=0",
                          headers=_headers(admin, make_token))
        assert resp.status_code == 422

    def test_dashboard_invalid_date_format_returns_422(self, client, admin, make_token):
        resp = client.get("/dashboard/admin/analytics?start_date=bad",
                          headers=_headers(admin, make_token))
        assert resp.status_code == 422

    def test_activity_invalid_date_returns_422(self, client, employee, make_token):
        resp = client.get("/activities?start_date=2026-13-45",
                          headers=_headers(employee, make_token))
        assert resp.status_code == 422
