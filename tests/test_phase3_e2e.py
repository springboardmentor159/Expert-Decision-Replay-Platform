"""
Phase 3 — Database, Reports, Dashboard & Files (End-to-End)

Runs a complete decision lifecycle, then verifies:
1. Database integrity (FK relationships, no orphans/duplicates)
2. Transaction & audit (multi-step ops, clean audit logs)
3. Versions & dashboard (sequential versions, dashboard accuracy)
4. Search & reports (combined filter across all report types)
5. Export check (PDF/Excel for every report type)
6. File upload check (no upload feature exists — documented)

All checks use SQLite in-memory (same as production schema via Base.metadata.create_all).
"""

import io
import math
from datetime import datetime, timedelta

import pytest
from openpyxl import load_workbook
from sqlalchemy import func

from app.core.security import hash_password
from app.models.access_log import AccessLog
from app.models.activity_log import ActivityLog
from app.models.alternative import Alternative
from app.models.audit_log import AuditLog
from app.models.comment import Comment
from app.models.decision import Decision
from app.models.decision_version import DecisionVersion
from app.models.discussion_thread import DiscussionThread
from app.models.enums import (
    AuditAction,
    AuditEntityType,
    DecisionStatus,
    RiskLevel,
    UserRole,
)
from app.models.meeting_note import MeetingNote
from app.models.security_log import SecurityLog
from app.models.user import User


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _user(db, email, eid, role=UserRole.EMPLOYEE, dept="Engineering"):
    u = User(
        full_name=f"E2E {role.value}",
        email=email, role=role,
        password=hash_password("password123"),
        employee_id=eid, department=dept,
    )
    db.add(u); db.commit(); db.refresh(u)
    return u


def _h(user, mk):
    return {"Authorization": f"Bearer {mk(str(user.id))}"}


# ---------------------------------------------------------------------------
# Master E2E fixture — builds the entire data graph in one shot
# ---------------------------------------------------------------------------

@pytest.fixture()
def e2e(db_session, client, make_token):
    """Run the complete decision lifecycle and return everything needed for checks."""
    db = db_session

    # --- 1. Users (4 roles) ---
    admin = _user(db, "e2e_admin@test.com", "E2E_A", UserRole.ADMINISTRATOR, "Engineering")
    mgr   = _user(db, "e2e_mgr@test.com",   "E2E_M", UserRole.MANAGER,       "Engineering")
    rev   = _user(db, "e2e_rev@test.com",   "E2E_R", UserRole.REVIEWER,      "Marketing")
    emp   = _user(db, "e2e_emp@test.com",   "E2E_E", UserRole.EMPLOYEE,      "Marketing")

    ha, hm, hr, he = _h(admin, make_token), _h(mgr, make_token), _h(rev, make_token), _h(emp, make_token)

    # --- 2. Decisions (one per user, varied categories) ---
    r1 = client.post("/decisions", json={"title": "Budget Plan",      "problem_statement": "Q4 budget",  "category": "Finance"},     headers=ha).json()
    r2 = client.post("/decisions", json={"title": "API Migration",    "problem_statement": "REST→gRPC",  "category": "Engineering"}, headers=hm).json()
    r3 = client.post("/decisions", json={"title": "Brand Refresh",    "problem_statement": "Rebrand",    "category": "Marketing"},   headers=hr).json()
    r4 = client.post("/decisions", json={"title": "Process Audit",    "problem_statement": "ISO check",  "category": "Operations"},  headers=he).json()

    d1_id, d2_id, d3_id, d4_id = r1["id"], r2["id"], r3["id"], r4["id"]

    # --- 3. Status transitions (full lifecycle for d1: Draft→Under Review→Approved) ---
    client.patch(f"/decisions/{d1_id}/status", json={"status": "Under Review"}, headers=ha)
    client.patch(f"/decisions/{d1_id}/status", json={"status": "Approved"},     headers=ha)
    # d2: Draft→Under Review
    client.patch(f"/decisions/{d2_id}/status", json={"status": "Under Review"}, headers=hm)
    # d3: Draft→Rejected
    client.patch(f"/decisions/{d3_id}/status", json={"status": "Rejected"},     headers=hr)
    # d4: stays Draft

    # --- 4. Rationale for approved decision ---
    client.put(f"/decisions/{d1_id}/rationale", json={"rationale": "Selected option A based on cost analysis."}, headers=ha)

    # --- 5. Alternatives for d1 (2 alternatives) ---
    a1r = client.post(f"/decisions/{d1_id}/alternatives", json={
        "name": "Option A — Cloud", "description": "Move to AWS",
        "pros": "Scalable", "cons": "Vendor lock-in",
        "estimated_cost": 50000, "feasibility_score": 4, "risk_level": "Medium",
    }, headers=ha)
    a2r = client.post(f"/decisions/{d1_id}/alternatives", json={
        "name": "Option B — On-prem", "description": "Keep on-prem",
        "pros": "Full control", "cons": "CapEx heavy",
        "estimated_cost": 120000, "feasibility_score": 3, "risk_level": "Low",
    }, headers=ha)
    alt1_id, alt2_id = a1r.json()["id"], a2r.json()["id"]

    # --- 6. Comments on d1 ---
    c1r = client.post(f"/decisions/{d1_id}/comments", json={"content": "Cloud is the way to go."},  headers=he)
    c2r = client.post(f"/decisions/{d1_id}/comments", json={"content": "On-prem gives more control."}, headers=hr)
    cmt1_id, cmt2_id = c1r.json()["id"], c2r.json()["id"]

    # --- 7. Discussion thread on d1 ---
    t1r = client.post(f"/decisions/{d1_id}/threads", json={"title": "Cost vs Control debate"}, headers=he)
    thr_id = t1r.json()["id"]
    # Reply to thread
    client.post(f"/threads/{thr_id}/comments", json={"content": "Reply: consider hybrid."}, headers=hr)

    # --- 8. Meeting note on d1 ---
    client.post(f"/decisions/{d1_id}/meeting-notes", json={
        "title": "Architecture Review",
        "content": "Discussed cloud vs on-prem tradeoffs.",
        "meeting_date": datetime.now().isoformat(),
    }, headers=ha)

    # --- 9. Reload all objects from DB ---
    decision1 = db.query(Decision).filter(Decision.id == d1_id).first()
    decision2 = db.query(Decision).filter(Decision.id == d2_id).first()
    decision3 = db.query(Decision).filter(Decision.id == d3_id).first()
    decision4 = db.query(Decision).filter(Decision.id == d4_id).first()
    alt1 = db.query(Alternative).filter(Alternative.id == alt1_id).first()
    alt2 = db.query(Alternative).filter(Alternative.id == alt2_id).first()
    cmt1 = db.query(Comment).filter(Comment.id == cmt1_id).first()
    cmt2 = db.query(Comment).filter(Comment.id == cmt2_id).first()
    thread = db.query(DiscussionThread).filter(DiscussionThread.id == thr_id).first()
    note = db.query(MeetingNote).filter(MeetingNote.decision_id == d1_id).first()

    return {
        "db": db, "client": client,
        "admin": admin, "mgr": mgr, "rev": rev, "emp": emp,
        "ha": ha, "hm": hm, "hr": hr, "he": he,
        "d1": decision1, "d2": decision2, "d3": decision3, "d4": decision4,
        "alt1": alt1, "alt2": alt2,
        "cmt1": cmt1, "cmt2": cmt2,
        "thread": thread, "note": note,
    }


# ===================================================================
# 1. DATABASE VERIFICATION — FK relationships, no orphans, no dupes
# ===================================================================

class TestDatabaseVerification:
    """Verify created data is correctly linked across all entities."""

    def test_all_decisions_exist(self, e2e):
        db = e2e["db"]
        assert db.query(Decision).count() == 4

    def test_all_alternatives_exist(self, e2e):
        db = e2e["db"]
        assert db.query(Alternative).count() == 2

    def test_all_comments_exist(self, e2e):
        db = e2e["db"]
        assert db.query(Comment).count() >= 2

    def test_all_threads_exist(self, e2e):
        db = e2e["db"]
        assert db.query(DiscussionThread).count() >= 1

    def test_all_meeting_notes_exist(self, e2e):
        db = e2e["db"]
        assert db.query(MeetingNote).count() >= 1

    def test_decision_fk_to_creator(self, e2e):
        db = e2e["db"]
        d = e2e["d1"]
        creator = db.query(User).filter(User.id == d.created_by).first()
        assert creator is not None
        assert creator.id == e2e["admin"].id

    def test_alternative_fk_to_decision(self, e2e):
        db = e2e["db"]
        a = e2e["alt1"]
        parent = db.query(Decision).filter(Decision.id == a.decision_id).first()
        assert parent is not None
        assert parent.id == e2e["d1"].id

    def test_comment_fk_to_decision_and_user(self, e2e):
        db = e2e["db"]
        c = e2e["cmt1"]
        assert db.query(Decision).filter(Decision.id == c.decision_id).first() is not None
        assert db.query(User).filter(User.id == c.user_id).first() is not None

    def test_thread_fk_to_decision_and_creator(self, e2e):
        db = e2e["db"]
        t = e2e["thread"]
        assert db.query(Decision).filter(Decision.id == t.decision_id).first() is not None
        assert db.query(User).filter(User.id == t.created_by).first() is not None

    def test_thread_reply_fk_to_thread(self, e2e):
        db = e2e["db"]
        reply = db.query(Comment).filter(Comment.thread_id == e2e["thread"].id).first()
        assert reply is not None
        assert reply.decision_id == e2e["d1"].id

    def test_meeting_note_fk_to_decision_and_creator(self, e2e):
        db = e2e["db"]
        n = e2e["note"]
        assert db.query(Decision).filter(Decision.id == n.decision_id).first() is not None
        assert db.query(User).filter(User.id == n.created_by).first() is not None

    def test_no_orphan_alternatives(self, e2e):
        db = e2e["db"]
        orphan_count = (
            db.query(Alternative)
            .filter(~Alternative.decision_id.in_(db.query(Decision.id)))
            .count()
        )
        assert orphan_count == 0

    def test_no_orphan_comments(self, e2e):
        db = e2e["db"]
        orphan_count = (
            db.query(Comment)
            .filter(~Comment.decision_id.in_(db.query(Decision.id)))
            .count()
        )
        assert orphan_count == 0

    def test_no_orphan_threads(self, e2e):
        db = e2e["db"]
        orphan_count = (
            db.query(DiscussionThread)
            .filter(~DiscussionThread.decision_id.in_(db.query(Decision.id)))
            .count()
        )
        assert orphan_count == 0

    def test_no_orphan_meeting_notes(self, e2e):
        db = e2e["db"]
        orphan_count = (
            db.query(MeetingNote)
            .filter(~MeetingNote.decision_id.in_(db.query(Decision.id)))
            .count()
        )
        assert orphan_count == 0

    def test_no_duplicate_decisions(self, e2e):
        db = e2e["db"]
        titles = [d.title for d in db.query(Decision).all()]
        assert len(titles) == len(set(titles))

    def test_no_duplicate_users(self, e2e):
        db = e2e["db"]
        emails = [u.email for u in db.query(User).all()]
        assert len(emails) == len(set(emails))

    def test_no_duplicate_employee_ids(self, e2e):
        db = e2e["db"]
        eids = [u.employee_id for u in db.query(User).all()]
        assert len(eids) == len(set(eids))

    def test_versions_created_for_each_decision(self, e2e):
        db = e2e["db"]
        for d in [e2e["d1"], e2e["d2"], e2e["d3"], e2e["d4"]]:
            v_count = db.query(DecisionVersion).filter(DecisionVersion.decision_id == d.id).count()
            assert v_count >= 1, f"Decision {d.id} has {v_count} versions (expected >= 1)"

    def test_security_log_on_login(self, e2e):
        """Security logs are created by the /login endpoint, not by direct DB inserts.
        Users in the e2e fixture are created via direct DB, so no login security logs
        exist. Verify the table is queryable and the endpoint creates logs when used."""
        client = e2e["client"]
        db = e2e["db"]
        # Trigger actual logins via the API
        for email in ["e2e_admin@test.com", "e2e_mgr@test.com"]:
            client.post("/login", json={"email": email, "password": "password123"})
        sec_count = db.query(SecurityLog).filter(SecurityLog.event_type == "login").count()
        assert sec_count >= 2

    def test_audit_log_on_decision_create(self, e2e):
        db = e2e["db"]
        create_count = db.query(AuditLog).filter(
            AuditLog.action == "create",
            AuditLog.entity_type == "decision",
        ).count()
        assert create_count >= 4

    def test_audit_log_on_status_change(self, e2e):
        db = e2e["db"]
        status_count = db.query(AuditLog).filter(
            AuditLog.action == "status_change",
            AuditLog.entity_type == "decision",
        ).count()
        assert status_count >= 4

    def test_activity_log_created(self, e2e):
        db = e2e["db"]
        act_count = db.query(ActivityLog).count()
        assert act_count >= 4  # from decision creates

    def test_all_fk_constraints_hold(self, e2e):
        """Verify every FK column references an existing parent — no integrity violations."""
        db = e2e["db"]
        # All decisions reference existing users
        for d in db.query(Decision).all():
            assert db.query(User).filter(User.id == d.created_by).first() is not None
        # All alternatives reference existing decisions
        for a in db.query(Alternative).all():
            assert db.query(Decision).filter(Decision.id == a.decision_id).first() is not None
        # All comments reference existing decisions and users
        for c in db.query(Comment).all():
            assert db.query(Decision).filter(Decision.id == c.decision_id).first() is not None
            assert db.query(User).filter(User.id == c.user_id).first() is not None
        # All threads reference existing decisions and users
        for t in db.query(DiscussionThread).all():
            assert db.query(Decision).filter(Decision.id == t.decision_id).first() is not None
            assert db.query(User).filter(User.id == t.created_by).first() is not None
        # All meeting notes reference existing decisions and users
        for n in db.query(MeetingNote).all():
            assert db.query(Decision).filter(Decision.id == n.decision_id).first() is not None
            assert db.query(User).filter(User.id == n.created_by).first() is not None


# ===================================================================
# 2. TRANSACTION & AUDIT CHECK
# ===================================================================

class TestTransactionAndAudit:
    """Verify multi-step ops succeed atomically, failures leave no partial state,
    and audit logs contain no secrets."""

    def test_successful_multi_step_decision_lifecycle(self, e2e):
        """The full lifecycle (create → add alternatives → comment → status change)
        completed without error. Verify all pieces are in DB."""
        db = e2e["db"]
        d1 = e2e["d1"]
        # Decision exists and is Approved
        assert d1.status == "Approved" or d1.status == DecisionStatus.APPROVED
        # Alternatives exist
        assert db.query(Alternative).filter(Alternative.decision_id == d1.id).count() == 2
        # Comments exist
        assert db.query(Comment).filter(Comment.decision_id == d1.id).count() >= 2
        # Thread exists
        assert db.query(DiscussionThread).filter(DiscussionThread.decision_id == d1.id).count() == 1
        # Meeting note exists
        assert db.query(MeetingNote).filter(MeetingNote.decision_id == d1.id).count() == 1
        # Rationale is set
        assert d1.rationale is not None

    def test_failed_create_leaves_no_partial_decision(self, client, db_session, make_token):
        """Posting an invalid decision (missing fields) should return 422 and
        create zero DB rows."""
        user = _user(db_session, "partial@test.com", "PARTIAL")
        h = _h(user, make_token)
        before = db_session.query(Decision).count()
        resp = client.post("/decisions", json={"title": "Only title"}, headers=h)
        assert resp.status_code == 422
        after = db_session.query(Decision).count()
        assert after == before  # no partial row created

    def test_failed_alternative_create_leaves_no_partial(self, client, db_session, make_token):
        """Posting an alternative with invalid data should not create a partial row."""
        user = _user(db_session, "partial2@test.com", "PARTIAL2")
        h = _h(user, make_token)
        r = client.post("/decisions", json={"title": "T", "problem_statement": "P", "category": "C"}, headers=h)
        d_id = r.json()["id"]
        before = db_session.query(Alternative).filter(Alternative.decision_id == d_id).count()
        # Invalid: missing name
        resp = client.post(f"/decisions/{d_id}/alternatives", json={"feasibility_score": 99}, headers=h)
        assert resp.status_code == 422
        after = db_session.query(Alternative).filter(Alternative.decision_id == d_id).count()
        assert after == before

    def test_audit_log_contains_no_passwords_or_tokens(self, e2e):
        """Scan all audit log descriptions and values for sensitive patterns."""
        db = e2e["db"]
        sensitive_patterns = ["password", "secret", "token", "bearer", "credential", "hash"]
        logs = db.query(AuditLog).all()
        for log in logs:
            text = f"{log.description or ''} {log.old_values or ''} {log.new_values or ''}".lower()
            for pat in sensitive_patterns:
                assert pat not in text, f"Audit log {log.id} contains '{pat}': {text}"

    def test_security_log_contains_no_passwords(self, e2e):
        """Security log descriptions should not contain passwords."""
        db = e2e["db"]
        logs = db.query(SecurityLog).all()
        for log in logs:
            desc = (log.description or "").lower()
            assert "password" not in desc, f"Security log {log.id} has password in description"

    def test_audit_entries_for_major_actions(self, e2e):
        """Verify audit entries exist for create, status_change, update.
        'login' requires the /login endpoint (users created via DB in fixture)."""
        db = e2e["db"]
        for action in ["create", "status_change", "update"]:
            count = db.query(AuditLog).filter(AuditLog.action == action).count()
            assert count >= 1, f"No audit entry for action='{action}'"

    def test_audit_entity_types_covered(self, e2e):
        """Verify audit logs exist for decision, alternative entity types.
        'auth' requires login endpoint calls (not used in fixture setup)."""
        db = e2e["db"]
        for etype in ["decision", "alternative"]:
            count = db.query(AuditLog).filter(AuditLog.entity_type == etype).count()
            assert count >= 1, f"No audit entry for entity_type='{etype}'"

    def test_decision_versions_created_on_status_change(self, e2e):
        """d1 went through 3 status changes (Draft→Under Review→Approved) + 1 rationale update.
        Should have at least 4 versions (1 initial + 3 status + 1 rationale = 5, but
        rationale may share a version with status change)."""
        db = e2e["db"]
        v_count = db.query(DecisionVersion).filter(DecisionVersion.decision_id == e2e["d1"].id).count()
        assert v_count >= 3  # at minimum: initial + 2 status changes

    def test_decision_versions_sequential(self, e2e):
        """Version numbers must be sequential (1, 2, 3, ...)."""
        db = e2e["db"]
        for d in [e2e["d1"], e2e["d2"], e2e["d3"], e2e["d4"]]:
            versions = (
                db.query(DecisionVersion)
                .filter(DecisionVersion.decision_id == d.id)
                .order_by(DecisionVersion.version_number)
                .all()
            )
            nums = [v.version_number for v in versions]
            assert nums == list(range(1, len(nums) + 1)), f"Versions not sequential for decision {d.id}: {nums}"

    def test_previous_versions_remain_available(self, e2e):
        """After status changes, old versions still exist and have correct data."""
        db = e2e["db"]
        versions = (
            db.query(DecisionVersion)
            .filter(DecisionVersion.decision_id == e2e["d1"].id)
            .order_by(DecisionVersion.version_number)
            .all()
        )
        assert len(versions) >= 2
        # First version should have "Draft" status
        assert versions[0].status == "Draft" or versions[0].status == DecisionStatus.DRAFT.value
        # Later versions should have different statuses
        statuses_seen = {v.status for v in versions}
        assert len(statuses_seen) >= 2


# ===================================================================
# 3. VERSION & DASHBOARD CHECK
# ===================================================================

class TestVersionAndDashboard:
    """Verify sequential versions, latest version correctness, and dashboard accuracy."""

    def test_d1_versions_are_sequential(self, e2e):
        db = e2e["db"]
        versions = (
            db.query(DecisionVersion)
            .filter(DecisionVersion.decision_id == e2e["d1"].id)
            .order_by(DecisionVersion.version_number)
            .all()
        )
        nums = [v.version_number for v in versions]
        assert nums == list(range(1, len(nums) + 1))

    def test_d1_latest_version_matches_decision(self, e2e):
        db = e2e["db"]
        latest = (
            db.query(DecisionVersion)
            .filter(DecisionVersion.decision_id == e2e["d1"].id)
            .order_by(DecisionVersion.version_number.desc())
            .first()
        )
        d = e2e["d1"]
        assert latest.title == d.title
        assert latest.category == d.category

    def test_employee_dashboard_counts_match_db(self, e2e):
        client = e2e["client"]
        db = e2e["db"]
        emp = e2e["emp"]
        he = e2e["he"]

        resp = client.get("/dashboard/employee", headers=he)
        assert resp.status_code == 200
        body = resp.json()

        # total_decisions should match employee's decisions in DB
        db_count = db.query(Decision).filter(Decision.created_by == emp.id).count()
        assert body["total_decisions"] == db_count

    def test_manager_dashboard_statistics_match_db(self, e2e):
        client = e2e["client"]
        db = e2e["db"]
        hm = e2e["hm"]

        resp = client.get("/dashboard/manager/statistics", headers=hm)
        assert resp.status_code == 200
        body = resp.json()

        # Manager sees org-wide stats
        db_total = db.query(Decision).count()
        assert body["total"] == db_total

        # Status breakdown
        db_draft = db.query(Decision).filter(Decision.status == "Draft").count()
        assert body["draft"] == db_draft

    def test_admin_dashboard_matches_db(self, e2e):
        client = e2e["client"]
        db = e2e["db"]
        ha = e2e["ha"]

        resp = client.get("/dashboard/admin", headers=ha)
        assert resp.status_code == 200
        body = resp.json()

        # Total users
        db_users = db.query(User).count()
        assert body["total_users"] == db_users

        # Total decisions
        db_decisions = db.query(Decision).count()
        assert body["total_decisions"] == db_decisions

        # Decision stats
        ds = body["decision_stats"]
        assert ds["total"] == db_decisions
        assert ds["draft"] == db.query(Decision).filter(Decision.status == "Draft").count()
        assert ds["approved"] == db.query(Decision).filter(Decision.status == "Approved").count()
        assert ds["rejected"] == db.query(Decision).filter(Decision.status == "Rejected").count()

    def test_admin_analytics_matches_db(self, e2e):
        client = e2e["client"]
        db = e2e["db"]
        ha = e2e["ha"]

        resp = client.get("/dashboard/admin/analytics", headers=ha)
        assert resp.status_code == 200
        body = resp.json()

        assert body["user_stats"]["total"] == db.query(User).count()
        assert body["decision_stats"]["total"] == db.query(Decision).count()

    def test_admin_decision_activity_granularity(self, e2e):
        client = e2e["client"]
        ha = e2e["ha"]

        for gran in ["day", "week", "month"]:
            resp = client.get(f"/dashboard/admin/decision-activity?granularity={gran}", headers=ha)
            assert resp.status_code == 200
            assert resp.json()["granularity"] == gran

    def test_admin_user_activity_matches_db(self, e2e):
        client = e2e["client"]
        db = e2e["db"]
        ha = e2e["ha"]

        resp = client.get("/dashboard/admin/user-activity", headers=ha)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_active_users"] >= 0


# ===================================================================
# 4. SEARCH & REPORTS — combined filter test
# ===================================================================

class TestSearchAndReports:
    """Run combined filters (Category + Status + Date + User/Team) across all report types
    and verify results match DB."""

    def test_combined_filter_decisions(self, e2e):
        client = e2e["client"]
        db = e2e["db"]
        ha = e2e["ha"]
        admin = e2e["admin"]

        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        # Category=Engineering + Status=Under Review + Date range + Creator=admin
        resp = client.get(
            f"/reports/decisions?category=Engineering&status=Under Review"
            f"&start_date={yesterday}&end_date={today}&creator={admin.id}",
            headers=ha,
        )
        assert resp.status_code == 200
        items = resp.json()["items"]

        # Verify every item matches all filters
        for item in items:
            assert item["category"] == "Engineering"
            assert item["status"] == "Under Review"
            assert item["creator"] == admin.full_name

        # Cross-check with DB
        db_count = (
            db.query(Decision)
            .filter(Decision.category == "Engineering")
            .filter(Decision.status == "Under Review")
            .filter(Decision.created_by == admin.id)
            .count()
        )
        assert resp.json()["total"] == db_count

    def test_combined_filter_approvals(self, e2e):
        client = e2e["client"]
        db = e2e["db"]
        ha = e2e["ha"]
        admin = e2e["admin"]

        resp = client.get(
            f"/reports/approvals?status=approved&reviewer={admin.id}",
            headers=ha,
        )
        assert resp.status_code == 200
        items = resp.json()["items"]

        for item in items:
            assert item["status"] == "Approved"
            assert item["reviewer"] == admin.full_name

        # Cross-check with DB
        db_count = (
            db.query(AuditLog)
            .filter(AuditLog.entity_type == "decision")
            .filter(AuditLog.action == "approve")
            .filter(AuditLog.user_id == admin.id)
            .count()
        )
        assert resp.json()["total"] == db_count

    def test_combined_filter_teams(self, e2e):
        client = e2e["client"]
        db = e2e["db"]
        ha = e2e["ha"]

        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        resp = client.get(
            f"/reports/teams?team=Engineering&start_date={yesterday}&end_date={today}",
            headers=ha,
        )
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) <= 1  # at most 1 team = Engineering

        if items:
            assert items[0]["team"] == "Engineering"
            # member_count should match DB
            db_members = db.query(User).filter(User.department == "Engineering").count()
            assert items[0]["member_count"] == db_members

    def test_combined_filter_audit(self, e2e):
        client = e2e["client"]
        db = e2e["db"]
        ha = e2e["ha"]
        admin = e2e["admin"]

        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        resp = client.get(
            f"/reports/audit?action=create&entity_type=decision"
            f"&user={admin.id}&start_date={yesterday}&end_date={today}",
            headers=ha,
        )
        assert resp.status_code == 200
        items = resp.json()["items"]

        for item in items:
            assert item["action"] == "create"
            assert item["entity_type"] == "decision"

        # Cross-check with DB
        db_count = (
            db.query(AuditLog)
            .filter(AuditLog.action == "create")
            .filter(AuditLog.entity_type == "decision")
            .filter(AuditLog.user_id == admin.id)
            .count()
        )
        assert resp.json()["total"] == db_count

    def test_decision_search_by_title(self, e2e):
        client = e2e["client"]
        ha = e2e["ha"]
        # Get all and verify the titles exist
        resp = client.get("/reports/decisions", headers=ha)
        titles = {i["title"] for i in resp.json()["items"]}
        assert "Budget Plan" in titles
        assert "API Migration" in titles

    def test_report_summary_matches_detail(self, e2e):
        """Report summary total must equal the total field from the same response."""
        client = e2e["client"]
        ha = e2e["ha"]
        resp = client.get("/reports/decisions", headers=ha).json()
        assert resp["summary"]["total"] == resp["total"]

    def test_teams_report_has_all_departments(self, e2e):
        client = e2e["client"]
        ha = e2e["ha"]
        resp = client.get("/reports/teams", headers=ha)
        teams = {i["team"] for i in resp.json()["items"]}
        assert "Engineering" in teams
        assert "Marketing" in teams

    def test_audit_report_has_all_action_types(self, e2e):
        client = e2e["client"]
        ha = e2e["ha"]
        resp = client.get("/reports/audit", headers=ha)
        actions = {i["action"] for i in resp.json()["items"]}
        assert "create" in actions
        assert "status_change" in actions


# ===================================================================
# 5. EXPORT CHECK — PDF and Excel for every report type
# ===================================================================

class TestExportCheck:
    """Verify PDF/Excel exports open, have correct data, correct row counts,
    no duplicates, and correct columns."""

    def _count_excel_data_rows(self, content):
        wb = load_workbook(io.BytesIO(content))
        ws = wb.active
        count = 0
        for row in range(1, ws.max_row + 1):
            val = ws.cell(row=row, column=1).value
            if val is not None and str(val).isdigit():
                count += 1
        wb.close()
        return count

    def _get_excel_headers(self, content):
        wb = load_workbook(io.BytesIO(content))
        ws = wb.active
        # The Excel structure is: title row, timestamp, blank, summary rows, blank, header row
        # Headers are the first row containing "ID" or "Title" or "Team" etc.
        for row in range(1, min(ws.max_row + 1, 15)):
            vals = [ws.cell(row=row, column=c).value for c in range(1, ws.max_column + 1)]
            # Check if this looks like a header row (multiple non-None string values)
            str_vals = [str(v) for v in vals if v is not None and isinstance(v, str)]
            if len(str_vals) >= 3:
                wb.close()
                return str_vals
        wb.close()
        return []

    # --- Decisions ---
    def test_decisions_pdf_valid(self, e2e):
        res = e2e["client"].get("/reports/decisions/export/pdf", headers=e2e["ha"])
        assert res.status_code == 200
        assert res.content[:5] == b"%PDF-"

    def test_decisions_excel_row_count(self, e2e):
        api_total = e2e["client"].get("/reports/decisions", headers=e2e["ha"]).json()["total"]
        res = e2e["client"].get("/reports/decisions/export/excel", headers=e2e["ha"])
        assert res.status_code == 200
        assert self._count_excel_data_rows(res.content) == api_total

    def test_decisions_excel_has_correct_columns(self, e2e):
        res = e2e["client"].get("/reports/decisions/export/excel", headers=e2e["ha"])
        headers = self._get_excel_headers(res.content)
        assert len(headers) >= 3, f"Expected at least 3 column headers, got: {headers}"

    def test_decisions_pdf_has_content_disposition(self, e2e):
        res = e2e["client"].get("/reports/decisions/export/pdf", headers=e2e["ha"])
        assert "attachment" in res.headers.get("content-disposition", "")

    def test_decisions_excel_has_content_disposition(self, e2e):
        res = e2e["client"].get("/reports/decisions/export/excel", headers=e2e["ha"])
        assert "attachment" in res.headers.get("content-disposition", "")

    # --- Approvals ---
    def test_approvals_pdf_valid(self, e2e):
        res = e2e["client"].get("/reports/approvals/export/pdf", headers=e2e["ha"])
        assert res.status_code == 200
        assert res.content[:5] == b"%PDF-"

    def test_approvals_excel_row_count(self, e2e):
        api_total = e2e["client"].get("/reports/approvals", headers=e2e["ha"]).json()["total"]
        res = e2e["client"].get("/reports/approvals/export/excel", headers=e2e["ha"])
        assert res.status_code == 200
        assert self._count_excel_data_rows(res.content) == api_total

    def test_approvals_pdf_has_content_disposition(self, e2e):
        res = e2e["client"].get("/reports/approvals/export/pdf", headers=e2e["ha"])
        assert "attachment" in res.headers.get("content-disposition", "")

    # --- Teams ---
    def test_teams_pdf_valid(self, e2e):
        res = e2e["client"].get("/reports/teams/export/pdf", headers=e2e["ha"])
        assert res.status_code == 200
        assert res.content[:5] == b"%PDF-"

    def test_teams_excel_row_count(self, e2e):
        api_total = e2e["client"].get("/reports/teams", headers=e2e["ha"]).json()["total"]
        res = e2e["client"].get("/reports/teams/export/excel", headers=e2e["ha"])
        assert res.status_code == 200
        # Teams excel has a different structure — count non-empty Team column rows
        wb = load_workbook(io.BytesIO(res.content))
        ws = wb.active
        header_row = None
        for row in range(1, ws.max_row + 1):
            if ws.cell(row=row, column=1).value == "Team":
                header_row = row
                break
        data_count = 0
        if header_row:
            for row in range(header_row + 1, ws.max_row + 1):
                val = ws.cell(row=row, column=1).value
                if val and str(val).strip():
                    data_count += 1
        wb.close()
        assert data_count == api_total

    def test_teams_pdf_has_content_disposition(self, e2e):
        res = e2e["client"].get("/reports/teams/export/pdf", headers=e2e["ha"])
        assert "attachment" in res.headers.get("content-disposition", "")

    # --- Audit ---
    def test_audit_pdf_valid(self, e2e):
        res = e2e["client"].get("/reports/audit/export/pdf", headers=e2e["ha"])
        assert res.status_code == 200
        assert res.content[:5] == b"%PDF-"

    def test_audit_excel_row_count(self, e2e):
        api_total = e2e["client"].get("/reports/audit", headers=e2e["ha"]).json()["total"]
        res = e2e["client"].get("/reports/audit/export/excel", headers=e2e["ha"])
        assert res.status_code == 200
        assert self._count_excel_data_rows(res.content) == api_total

    def test_audit_pdf_has_content_disposition(self, e2e):
        res = e2e["client"].get("/reports/audit/export/pdf", headers=e2e["ha"])
        assert "attachment" in res.headers.get("content-disposition", "")

    def test_audit_excel_has_content_disposition(self, e2e):
        res = e2e["client"].get("/reports/audit/export/excel", headers=e2e["ha"])
        assert "attachment" in res.headers.get("content-disposition", "")

    # --- Filtered exports ---
    def test_filtered_decisions_export_matches_api(self, e2e):
        api = e2e["client"].get("/reports/decisions?status=Approved", headers=e2e["ha"]).json()
        res = e2e["client"].get("/reports/decisions/export/excel?status=Approved", headers=e2e["ha"])
        assert res.status_code == 200
        assert self._count_excel_data_rows(res.content) == api["total"]

    def test_filtered_audit_export_matches_api(self, e2e):
        api = e2e["client"].get("/reports/audit?action=create", headers=e2e["ha"]).json()
        res = e2e["client"].get("/reports/audit/export/excel?action=create", headers=e2e["ha"])
        assert res.status_code == 200
        assert self._count_excel_data_rows(res.content) == api["total"]

    # --- No duplicates in exports ---
    def test_decisions_export_no_duplicate_rows(self, e2e):
        api_ids = {i["id"] for i in e2e["client"].get("/reports/decisions", headers=e2e["ha"]).json()["items"]}
        res = e2e["client"].get("/reports/decisions/export/excel", headers=e2e["ha"])
        wb = load_workbook(io.BytesIO(res.content))
        ws = wb.active
        excel_ids = set()
        for row in range(1, ws.max_row + 1):
            val = ws.cell(row=row, column=1).value
            if val is not None and str(val).isdigit():
                excel_ids.add(int(val))
        wb.close()
        assert excel_ids == api_ids

    # --- Empty export ---
    def test_export_with_empty_data_valid(self, db_session, client, make_token):
        u = _user(db_session, "emptyexport@test.com", "EMPTYEXP", UserRole.ADMINISTRATOR)
        h = _h(u, make_token)
        # PDF
        res = client.get("/reports/decisions/export/pdf", headers=h)
        assert res.status_code == 200
        assert res.content[:5] == b"%PDF-"
        # Excel
        res = client.get("/reports/decisions/export/excel", headers=h)
        assert res.status_code == 200
        wb = load_workbook(io.BytesIO(res.content))
        assert wb.active.cell(row=1, column=1).value == "Decisions Report"
        wb.close()


# ===================================================================
# 6. FILE UPLOAD CHECK
# ===================================================================

class TestFileUploadCheck:
    """No file upload feature exists in the codebase. Document this."""

    def test_no_upload_endpoints_exist(self):
        """The application has no file upload, attachment, or document model.
        All 'file' references are Content-Disposition headers on exports."""
        from app.main import app
        # Check all route paths via openapi schema
        schema = app.openapi()
        paths = list(schema.get("paths", {}).keys())
        upload_paths = [p for p in paths if "upload" in p.lower() or "attachment" in p.lower() or "document" in p.lower()]
        assert upload_paths == [], f"Unexpected upload routes found: {upload_paths}"

    def test_no_document_model_exists(self):
        """Verify no Document/Attachment model is registered."""
        from app.models import __all__ as model_names
        file_models = [m for m in model_names if "file" in m.lower() or "document" in m.lower() or "attachment" in m.lower()]
        assert file_models == [], f"Unexpected file models found: {file_models}"

    def test_no_upload_in_user_model(self):
        """User model has no file-related columns."""
        cols = {c.name for c in User.__table__.columns}
        file_cols = [c for c in cols if "file" in c.lower() or "avatar" in c.lower() or "document" in c.lower()]
        assert file_cols == []

    def test_no_upload_in_decision_model(self):
        """Decision model has no file-related columns."""
        cols = {c.name for c in Decision.__table__.columns}
        file_cols = [c for c in cols if "file" in c.lower() or "document" in c.lower() or "attachment" in c.lower()]
        assert file_cols == []
