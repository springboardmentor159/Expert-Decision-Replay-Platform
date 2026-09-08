"""
Sprint 13 — Phase 1: System Review & Integration Test Suite

Tests the end-to-end integration workflow:
Login -> Create Decision -> Add Alternatives -> Discussion -> Submit -> Reviewer Approval -> Manager Approval -> Final Decision -> Audit -> Dashboard -> Report

Verifies:
- Data passing between all modules
- User and decision linkage
- Decision status state machine
- Audit and activity record creation
- Role-based permissions across Employee, Reviewer, Manager, Administrator
- Database record creation and integrity
- Standard HTTP response codes: 200, 201, 404, 401, 403, 422
"""

import io
import json
import pytest
from openpyxl import load_workbook

from app.core.security import hash_password
from app.models.audit_log import AuditLog
from app.models.activity_log import ActivityLog
from app.models.decision import Decision
from app.models.decision_version import DecisionVersion
from app.models.alternative import Alternative
from app.models.comment import Comment
from app.models.discussion_thread import DiscussionThread
from app.models.meeting_note import MeetingNote
from app.models.enums import UserRole, DecisionStatus, RiskLevel, AuditAction, AuditEntityType
from app.models.user import User


# ==============================================================================
# Helpers
# ==============================================================================

def _create_user(db_session, email, employee_id, role=UserRole.EMPLOYEE, department="Engineering"):
    user = User(
        full_name=f"User {employee_id}",
        email=email,
        role=role,
        password=hash_password("Password123!"),
        employee_id=employee_id,
        department=department,
        designation="Staff Engineer",
        phone_number="555-0100",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ==============================================================================
# Main Flow End-to-End Integration Test
# ==============================================================================

class TestMainFlowIntegration:
    """
    Validates:
    Login -> Create Decision -> Add Alternatives -> Discussion -> Submit ->
    Reviewer Approval -> Manager Approval -> Final Decision -> Audit -> Dashboard -> Report
    """

    def test_complete_main_flow(self, client, db_session):
        # ----------------------------------------------------------------------
        # 1. SETUP & LOGIN
        # ----------------------------------------------------------------------
        admin = _create_user(db_session, "alice_admin@test.com", "EMP_ADM", UserRole.ADMINISTRATOR, "Engineering")
        mgr = _create_user(db_session, "bob_manager@test.com", "EMP_MGR", UserRole.MANAGER, "Engineering")
        rev = _create_user(db_session, "dave_reviewer@test.com", "EMP_REV", UserRole.REVIEWER, "Architecture")
        emp = _create_user(db_session, "carol_employee@test.com", "EMP_EMP", UserRole.EMPLOYEE, "Engineering")

        # Login as all 4 users
        login_emp = client.post("/login", json={"email": "carol_employee@test.com", "password": "Password123!"})
        assert login_emp.status_code == 200
        emp_token = login_emp.json()["access_token"]
        assert login_emp.json()["user"]["role"] == "Employee"

        login_rev = client.post("/login", json={"email": "dave_reviewer@test.com", "password": "Password123!"})
        assert login_rev.status_code == 200
        rev_token = login_rev.json()["access_token"]
        assert login_rev.json()["user"]["role"] == "Reviewer"

        login_mgr = client.post("/login", json={"email": "bob_manager@test.com", "password": "Password123!"})
        assert login_mgr.status_code == 200
        mgr_token = login_mgr.json()["access_token"]
        assert login_mgr.json()["user"]["role"] == "Manager"

        login_adm = client.post("/login", json={"email": "alice_admin@test.com", "password": "Password123!"})
        assert login_adm.status_code == 200
        adm_token = login_adm.json()["access_token"]
        assert login_adm.json()["user"]["role"] == "Administrator"

        h_emp = _auth_headers(emp_token)
        h_rev = _auth_headers(rev_token)
        h_mgr = _auth_headers(mgr_token)
        h_adm = _auth_headers(adm_token)

        # ----------------------------------------------------------------------
        # 2. CREATE DECISION (Employee)
        # ----------------------------------------------------------------------
        create_dec_res = client.post(
            "/decisions",
            json={
                "title": "Migrate to Event-Driven Architecture",
                "problem_statement": "Monolith batch jobs cause latency; evaluate asynchronous messaging systems.",
                "category": "Architecture",
            },
            headers=h_emp,
        )
        assert create_dec_res.status_code == 201
        dec = create_dec_res.json()
        dec_id = dec["id"]
        assert dec["title"] == "Migrate to Event-Driven Architecture"
        assert dec["status"] == "Draft"
        assert dec["created_by"] == emp.id

        # Verify initial v1 snapshot was automatically created
        v1_res = client.get(f"/decisions/{dec_id}/versions/1", headers=h_emp)
        assert v1_res.status_code == 200
        assert v1_res.json()["version_number"] == 1
        assert v1_res.json()["status"] == "Draft"

        # Verify audit & activity records created for decision creation
        create_audits = db_session.query(AuditLog).filter(
            AuditLog.entity_type == "decision",
            AuditLog.entity_id == dec_id,
            AuditLog.action == "create",
        ).all()
        assert len(create_audits) == 1
        assert create_audits[0].user_id == emp.id

        # ----------------------------------------------------------------------
        # 3. ADD ALTERNATIVES (Employee)
        # ----------------------------------------------------------------------
        alt1_res = client.post(
            f"/decisions/{dec_id}/alternatives",
            json={
                "name": "Apache Kafka",
                "description": "High-throughput distributed event streaming platform",
                "pros": "Horizontally scalable, partitioned log model, durable replay",
                "cons": "Operational complexity, ZooKeeper/KRaft cluster overhead",
                "estimated_cost": 25000,
                "feasibility_score": 4,
                "risk_level": "Medium",
            },
            headers=h_emp,
        )
        assert alt1_res.status_code == 201
        alt1_id = alt1_res.json()["id"]
        assert alt1_res.json()["decision_id"] == dec_id

        alt2_res = client.post(
            f"/decisions/{dec_id}/alternatives",
            json={
                "name": "RabbitMQ",
                "description": "Traditional AMQP message broker",
                "pros": "Low latency, complex routing topologies, lightweight",
                "cons": "Limited message replay, lower partition throughput",
                "estimated_cost": 12000,
                "feasibility_score": 5,
                "risk_level": "Low",
            },
            headers=h_emp,
        )
        assert alt2_res.status_code == 201
        alt2_id = alt2_res.json()["id"]

        # Verify side-by-side comparison
        compare_res = client.get(f"/decisions/{dec_id}/alternatives/compare", headers=h_emp)
        assert compare_res.status_code == 200
        alts_in_compare = compare_res.json()["alternatives"]
        assert len(alts_in_compare) == 2
        assert {a["name"] for a in alts_in_compare} == {"Apache Kafka", "RabbitMQ"}

        # ----------------------------------------------------------------------
        # 4. DISCUSSION & COLLABORATION (All roles)
        # ----------------------------------------------------------------------
        # 4a. Employee posts initial comment
        c1_res = client.post(
            f"/decisions/{dec_id}/comments",
            json={"content": "I recommend RabbitMQ for lower maintenance overhead."},
            headers=h_emp,
        )
        assert c1_res.status_code == 201
        c1_id = c1_res.json()["id"]

        # 4b. Reviewer opens a discussion thread
        t1_res = client.post(
            f"/decisions/{dec_id}/threads",
            json={
                "title": "Throughput Scaling Analysis",
                "description": "Will RabbitMQ sustain peak load of 100k msg/sec during holiday campaigns?",
            },
            headers=h_rev,
        )
        assert t1_res.status_code == 201
        t1_id = t1_res.json()["id"]

        # 4c. Manager replies to the thread
        reply_res = client.post(
            f"/threads/{t1_id}/comments",
            json={"content": "Historical data shows peak load reaches 120k msg/sec. Kafka handles this safely."},
            headers=h_mgr,
        )
        assert reply_res.status_code == 201

        # 4d. Manager records an Architecture Review Meeting Note
        note_res = client.post(
            f"/decisions/{dec_id}/meeting-notes",
            json={
                "title": "Architecture Evaluation Review",
                "content": "Attendees: Alice, Bob, Carol, Dave. Consensus reached on Kafka for long-term scalability.",
                "meeting_date": "2026-09-08T10:00:00Z",
            },
            headers=h_mgr,
        )
        assert note_res.status_code == 201
        note_id = note_res.json()["id"]

        # ----------------------------------------------------------------------
        # 5. SUBMIT DECISION (Employee)
        # ----------------------------------------------------------------------
        submit_res = client.patch(
            f"/decisions/{dec_id}/status",
            json={"status": "Under Review"},
            headers=h_emp,
        )
        assert submit_res.status_code == 200
        assert submit_res.json()["status"] == "Under Review"

        # Verify version snapshot v2 created
        v2_res = client.get(f"/decisions/{dec_id}/versions/2", headers=h_emp)
        assert v2_res.status_code == 200
        assert v2_res.json()["status"] == "Draft"  # snapshot captured pre-transition status

        # ----------------------------------------------------------------------
        # 6. REVIEWER APPROVAL / ENDORSEMENT (Reviewer)
        # ----------------------------------------------------------------------
        # Reviewer adds formal endorsement comment
        rev_review_res = client.post(
            f"/decisions/{dec_id}/comments",
            json={"content": "REVIEWER APPROVAL: Technical risk assessment complete. Kafka architecture endorsed."},
            headers=h_rev,
        )
        assert rev_review_res.status_code == 201

        # ----------------------------------------------------------------------
        # 7. MANAGER APPROVAL & FINAL DECISION (Manager)
        # ----------------------------------------------------------------------
        # Manager approves status
        mgr_approve_res = client.patch(
            f"/decisions/{dec_id}/status",
            json={"status": "Approved"},
            headers=h_mgr,
        )
        assert mgr_approve_res.status_code == 200
        assert mgr_approve_res.json()["status"] == "Approved"

        # Creator updates rationale
        rationale_res = client.put(
            f"/decisions/{dec_id}/rationale",
            json={
                "rationale": "Kafka selected due to high throughput requirements (>100k msg/sec) and multi-region replay capabilities."
            },
            headers=h_emp,
        )
        assert rationale_res.status_code == 200
        assert "Kafka selected" in rationale_res.json()["rationale"]

        # ----------------------------------------------------------------------
        # 8. AUDIT TRAIL VERIFICATION
        # ----------------------------------------------------------------------
        history_res = client.get(f"/decisions/{dec_id}/history", headers=h_emp)
        assert history_res.status_code == 200
        audit_items = history_res.json()["items"]
        assert len(audit_items) >= 3  # create, status_change (Under Review), status_change (Approved), rationale update
        actions = [a["action"] for a in audit_items]
        assert "create" in actions
        assert "status_change" in actions

        # Verify all decision versions
        versions_res = client.get(f"/decisions/{dec_id}/versions", headers=h_emp)
        assert versions_res.status_code == 200
        versions = versions_res.json()["versions"]
        assert len(versions) >= 3

        # ----------------------------------------------------------------------
        # 9. DASHBOARDS VERIFICATION
        # ----------------------------------------------------------------------
        # 9a. Employee Dashboard
        emp_dash_res = client.get("/dashboard/employee", headers=h_emp)
        assert emp_dash_res.status_code == 200
        emp_dash = emp_dash_res.json()
        assert emp_dash["total_decisions"] >= 1
        approved_status = next((s for s in emp_dash["decisions_by_status"] if s["status"] == "Approved"), None)
        assert approved_status is not None and approved_status["count"] >= 1
        assert len(emp_dash["recent_activity"]) >= 1

        # 9b. Manager Dashboard Statistics
        mgr_dash_res = client.get("/dashboard/manager/statistics", headers=h_mgr)
        assert mgr_dash_res.status_code == 200
        mgr_dash = mgr_dash_res.json()
        assert mgr_dash["total"] >= 1
        assert mgr_dash["approved"] >= 1

        # 9c. Admin Dashboard
        adm_dash_res = client.get("/dashboard/admin", headers=h_adm)
        assert adm_dash_res.status_code == 200
        adm_dash = adm_dash_res.json()
        assert adm_dash["total_users"] >= 4
        assert adm_dash["total_decisions"] >= 1
        assert adm_dash["decision_stats"]["approved"] >= 1

        # 9d. Admin Analytics & Activity
        analytics_res = client.get("/dashboard/admin/analytics?start_date=2026-01-01&end_date=2026-12-31", headers=h_adm)
        assert analytics_res.status_code == 200
        dec_activity_res = client.get("/dashboard/admin/decision-activity?granularity=day", headers=h_adm)
        assert dec_activity_res.status_code == 200
        user_act_res = client.get("/dashboard/admin/user-activity", headers=h_adm)
        assert user_act_res.status_code == 200

        # ----------------------------------------------------------------------
        # 10. REPORTS & EXPORTS VERIFICATION
        # ----------------------------------------------------------------------
        # 10a. Decisions Report JSON
        rep_dec_res = client.get("/reports/decisions", headers=h_adm)
        assert rep_dec_res.status_code == 200
        dec_items = rep_dec_res.json()["items"]
        our_dec_rep = next((d for d in dec_items if d["id"] == dec_id), None)
        assert our_dec_rep is not None
        assert our_dec_rep["alternative_count"] == 2
        assert our_dec_rep["status"] == "Approved"
        assert our_dec_rep["creator"] == emp.full_name

        # 10b. Teams Report JSON
        rep_team_res = client.get("/reports/teams", headers=h_adm)
        assert rep_team_res.status_code == 200
        eng_team = next((t for t in rep_team_res.json()["items"] if t["team"] == "Engineering"), None)
        assert eng_team is not None
        assert eng_team["member_count"] >= 3
        assert eng_team["decision_count"] >= 1

        # 10c. Audit Report JSON
        rep_audit_res = client.get("/reports/audit", headers=h_adm)
        assert rep_audit_res.status_code == 200
        assert rep_audit_res.json()["total"] >= 5

        # 10d. PDF & Excel Exports
        pdf_res = client.get("/reports/decisions/export/pdf", headers=h_adm)
        assert pdf_res.status_code == 200
        assert pdf_res.content[:5] == b"%PDF-"

        excel_res = client.get("/reports/decisions/export/excel", headers=h_adm)
        assert excel_res.status_code == 200
        wb = load_workbook(io.BytesIO(excel_res.content))
        assert "Decisions" in wb.sheetnames


# ==============================================================================
# Basic API Response Codes (200, 201, 404, 401, 403, 422)
# ==============================================================================

class TestApiResponsesAndPermissions:
    """Verifies standard HTTP status codes and RBAC across all system endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self, client, db_session, make_token):
        self.client = client
        self.db = db_session
        self.adm = _create_user(db_session, "r_adm@test.com", "R_ADM", UserRole.ADMINISTRATOR)
        self.mgr = _create_user(db_session, "r_mgr@test.com", "R_MGR", UserRole.MANAGER)
        self.emp = _create_user(db_session, "r_emp@test.com", "R_EMP", UserRole.EMPLOYEE)
        self.other = _create_user(db_session, "r_other@test.com", "R_OTH", UserRole.EMPLOYEE)

        self.h_adm = {"Authorization": f"Bearer {make_token(str(self.adm.id))}"}
        self.h_mgr = {"Authorization": f"Bearer {make_token(str(self.mgr.id))}"}
        self.h_emp = {"Authorization": f"Bearer {make_token(str(self.emp.id))}"}
        self.h_other = {"Authorization": f"Bearer {make_token(str(self.other.id))}"}

    def test_200_successful_retrieval_and_update(self):
        # Create decision
        dec = self.client.post(
            "/decisions",
            json={"title": "Original Title", "problem_statement": "PS", "category": "General"},
            headers=self.h_emp,
        ).json()

        # 200 GET
        get_res = self.client.get(f"/decisions/{dec['id']}", headers=self.h_emp)
        assert get_res.status_code == 200
        assert get_res.json()["title"] == "Original Title"

        # 200 PUT update
        put_res = self.client.put(
            f"/decisions/{dec['id']}",
            json={"title": "Updated Title"},
            headers=self.h_emp,
        )
        assert put_res.status_code == 200
        assert put_res.json()["title"] == "Updated Title"

    def test_201_successful_creation(self):
        # User 201
        u_res = self.client.post("/users", json={
            "full_name": "New User",
            "email": "brand_new@test.com",
            "password": "Password123!",
            "role": "Employee",
            "employee_id": "NEW_001",
        })
        assert u_res.status_code == 201

        # Decision 201
        d_res = self.client.post(
            "/decisions",
            json={"title": "Created Dec", "problem_statement": "PS", "category": "Tech"},
            headers=self.h_emp,
        )
        assert d_res.status_code == 201
        did = d_res.json()["id"]

        # Alternative 201
        alt_res = self.client.post(
            f"/decisions/{did}/alternatives",
            json={"name": "Option A", "feasibility_score": 4, "risk_level": "Low"},
            headers=self.h_emp,
        )
        assert alt_res.status_code == 201

        # Comment 201
        com_res = self.client.post(f"/decisions/{did}/comments", json={"content": "Great start"}, headers=self.h_emp)
        assert com_res.status_code == 201

        # Thread 201
        thr_res = self.client.post(f"/decisions/{did}/threads", json={"title": "T1", "description": "D1"}, headers=self.h_emp)
        assert thr_res.status_code == 201
        tid = thr_res.json()["id"]

        # Thread reply 201
        rep_res = self.client.post(f"/threads/{tid}/comments", json={"content": "Reply 1"}, headers=self.h_emp)
        assert rep_res.status_code == 201

        # Meeting note 201
        note_res = self.client.post(
            f"/decisions/{did}/meeting-notes",
            json={"title": "Kickoff", "content": "Notes content", "meeting_date": "2026-09-08T10:00:00Z"},
            headers=self.h_emp,
        )
        assert note_res.status_code == 201

    def test_404_missing_resources(self):
        # Nonexistent decision
        assert self.client.get("/decisions/999999", headers=self.h_emp).status_code == 404
        assert self.client.put("/decisions/999999", json={"title": "X"}, headers=self.h_emp).status_code == 404
        assert self.client.patch("/decisions/999999/status", json={"status": "Under Review"}, headers=self.h_emp).status_code == 404
        assert self.client.post("/decisions/999999/alternatives", json={"name": "A"}, headers=self.h_emp).status_code == 404
        assert self.client.post("/decisions/999999/comments", json={"content": "C"}, headers=self.h_emp).status_code == 404
        assert self.client.get("/decisions/999999/versions", headers=self.h_emp).status_code == 404

        # Nonexistent alternative, comment, thread, meeting note
        assert self.client.get("/alternatives/999999", headers=self.h_emp).status_code == 404
        assert self.client.get("/comments/999999", headers=self.h_emp).status_code == 404
        assert self.client.get("/threads/999999", headers=self.h_emp).status_code == 404
        assert self.client.get("/meeting-notes/999999", headers=self.h_emp).status_code == 404
        assert self.client.get("/audit-logs/999999", headers=self.h_adm).status_code == 404

    def test_401_no_or_invalid_jwt(self):
        # No JWT
        assert self.client.get("/decisions").status_code == 401
        assert self.client.get("/dashboard/employee").status_code == 401
        assert self.client.get("/reports/decisions").status_code == 401

        # Invalid JWT
        bad_headers = {"Authorization": "Bearer completely.invalid.jwt"}
        assert self.client.get("/decisions", headers=bad_headers).status_code == 401
        assert self.client.get("/dashboard/employee", headers=bad_headers).status_code == 401

        # Bad login credentials
        bad_login = self.client.post("/login", json={"email": "r_emp@test.com", "password": "WrongPassword"})
        assert bad_login.status_code == 401

    def test_403_insufficient_permission(self):
        # 1. Employee cannot view Admin dashboard
        assert self.client.get("/dashboard/admin", headers=self.h_emp).status_code == 403
        assert self.client.get("/dashboard/admin/analytics", headers=self.h_emp).status_code == 403

        # 2. Employee cannot view Manager dashboard
        assert self.client.get("/dashboard/manager/statistics", headers=self.h_emp).status_code == 403

        # 3. Employee cannot view Security or Access logs
        assert self.client.get("/security/logs", headers=self.h_emp).status_code == 403
        assert self.client.get("/access/logs", headers=self.h_emp).status_code == 403

        # 4. Non-creator non-admin cannot update rationale
        dec = self.client.post(
            "/decisions",
            json={"title": "Carol Decision", "problem_statement": "PS", "category": "Tech"},
            headers=self.h_emp,
        ).json()
        rationale_res = self.client.put(
            f"/decisions/{dec['id']}/rationale",
            json={"rationale": "Hijacked Rationale"},
            headers=self.h_other,
        )
        assert rationale_res.status_code == 403

        # 5. Non-author non-admin cannot update or delete comments
        com = self.client.post(f"/decisions/{dec['id']}/comments", json={"content": "Carol Comment"}, headers=self.h_emp).json()
        assert self.client.put(f"/comments/{com['id']}", json={"content": "Other edit"}, headers=self.h_other).status_code == 403
        assert self.client.delete(f"/comments/{com['id']}", headers=self.h_other).status_code == 403

        # 6. Non-author non-admin cannot update or delete threads
        thr = self.client.post(f"/decisions/{dec['id']}/threads", json={"title": "Carol Thread", "description": "D"}, headers=self.h_emp).json()
        assert self.client.put(f"/threads/{thr['id']}", json={"title": "Other edit"}, headers=self.h_other).status_code == 403
        assert self.client.delete(f"/threads/{thr['id']}", headers=self.h_other).status_code == 403

        # 7. Non-author non-admin cannot update or delete meeting notes
        note = self.client.post(
            f"/decisions/{dec['id']}/meeting-notes",
            json={"title": "Carol Note", "content": "C", "meeting_date": "2026-09-08T10:00:00Z"},
            headers=self.h_emp,
        ).json()
        assert self.client.put(f"/meeting-notes/{note['id']}", json={"content": "Other edit"}, headers=self.h_other).status_code == 403
        assert self.client.delete(f"/meeting-notes/{note['id']}", headers=self.h_other).status_code == 403

    def test_422_invalid_inputs(self):
        dec = self.client.post(
            "/decisions",
            json={"title": "Valid Dec", "problem_statement": "PS", "category": "General"},
            headers=self.h_emp,
        ).json()

        # 1. Missing required field in Decision creation (missing problem_statement)
        res1 = self.client.post("/decisions", json={"title": "Incomplete"}, headers=self.h_emp)
        assert res1.status_code == 422

        # 2. Invalid status in patch status
        res2 = self.client.patch(f"/decisions/{dec['id']}/status", json={"status": "NonexistentStatus"}, headers=self.h_emp)
        assert res2.status_code == 422

        # 3. Invalid feasibility score in Alternative (> 5)
        res3 = self.client.post(
            f"/decisions/{dec['id']}/alternatives",
            json={"name": "Alt", "feasibility_score": 10, "risk_level": "Low"},
            headers=self.h_emp,
        )
        assert res3.status_code == 422

        # 4. Invalid risk level in Alternative
        res4 = self.client.post(
            f"/decisions/{dec['id']}/alternatives",
            json={"name": "Alt", "feasibility_score": 4, "risk_level": "SuperHigh"},
            headers=self.h_emp,
        )
        assert res4.status_code == 422

        # 5. Invalid date format in reports
        res5 = self.client.get("/reports/decisions?start_date=bad-date", headers=self.h_adm)
        assert res5.status_code == 422

        # 6. Reversed date range in reports
        res6 = self.client.get("/reports/decisions?start_date=2026-12-31&end_date=2026-01-01", headers=self.h_adm)
        assert res6.status_code == 422

        # 7. Invalid pagination parameter (page=0)
        res7 = self.client.get("/reports/decisions?page=0", headers=self.h_adm)
        assert res7.status_code == 422
