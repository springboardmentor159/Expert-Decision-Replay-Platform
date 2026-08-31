import json
from datetime import date, datetime, timedelta

from app.models.audit_log import AuditLog
from app.models.decision import Decision
from app.models.decision_version import DecisionVersion
from app.models.security_log import SecurityLog
from app.models.access_log import AccessLog
from app.models.enums import UserRole, DecisionStatus
from app.models.user import User
from app.core.security import hash_password


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _create_user(db_session, email, employee_id, role=UserRole.EMPLOYEE):
    user = User(
        full_name=f"User {employee_id}",
        email=email,
        role=role,
        password=hash_password("password123"),
        employee_id=employee_id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _auth_headers(user, make_token):
    token = make_token(str(user.id))
    return {"Authorization": f"Bearer {token}"}


def _login(client, email, password="password123"):
    resp = client.post("/login", json={"email": email, "password": password})
    return resp


def _create_decision(client, headers, title="Test Decision", category="Engineering"):
    resp = client.post(
        "/decisions",
        json={"title": title, "problem_statement": "PS", "category": category},
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def _update_decision(client, headers, decision_id, title="Updated Decision"):
    resp = client.put(
        f"/decisions/{decision_id}",
        json={"title": title},
        headers=headers,
    )
    return resp


def _change_status(client, headers, decision_id, new_status):
    resp = client.patch(
        f"/decisions/{decision_id}/status",
        json={"status": new_status},
        headers=headers,
    )
    return resp


def _create_alternative(client, headers, decision_id, name="Alt A"):
    resp = client.post(
        f"/decisions/{decision_id}/alternatives",
        json={
            "name": name,
            "description": "desc",
            "pros": "pro",
            "cons": "con",
            "estimated_cost": 100,
            "feasibility_score": 4,
            "risk_level": "Low",
        },
        headers=headers,
    )
    return resp


def _create_comment(client, headers, decision_id, content="Great idea"):
    resp = client.post(
        f"/decisions/{decision_id}/comments",
        json={"content": content},
        headers=headers,
    )
    return resp


# ============================================================
# 1. LOGIN WORKFLOW — Security + Audit logs
# ============================================================

def test_login_creates_security_and_audit_logs(client, db_session, make_token):
    user = _create_user(db_session, "wf_login@example.com", "EMP_WF_LOG")

    resp = _login(client, "wf_login@example.com")
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    sec_logs = (
        db_session.query(SecurityLog)
        .filter(SecurityLog.event_type == "login", SecurityLog.user_id == user.id)
        .all()
    )
    assert len(sec_logs) >= 1

    audit_logs = (
        db_session.query(AuditLog)
        .filter(AuditLog.user_id == user.id, AuditLog.action == "login")
        .all()
    )
    assert len(audit_logs) >= 1


def test_login_failed_creates_security_log(client, db_session, make_token):
    _create_user(db_session, "wf_fail@example.com", "EMP_WF_FAIL")

    resp = _login(client, "wf_fail@example.com", "wrongpassword")
    assert resp.status_code == 401

    sec_logs = (
        db_session.query(SecurityLog)
        .filter(SecurityLog.event_type == "login_failed")
        .all()
    )
    assert len(sec_logs) >= 1


def test_logout_creates_security_and_audit_logs(client, db_session, make_token):
    user = _create_user(db_session, "wf_logout@example.com", "EMP_WF_LOGO")

    resp = _login(client, "wf_logout@example.com")
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/login/logout", headers=headers)
    assert resp.status_code == 200

    sec_logs = (
        db_session.query(SecurityLog)
        .filter(SecurityLog.event_type == "logout", SecurityLog.user_id == user.id)
        .all()
    )
    assert len(sec_logs) >= 1


# ============================================================
# 2. CREATE DECISION — Audit + DecisionVersion (v1)
# ============================================================

def test_create_decision_creates_audit_and_version(client, db_session, make_token):
    user = _create_user(db_session, "wf_crtdec@example.com", "EMP_WF_CD")
    headers = _auth_headers(user, make_token)

    did = _create_decision(client, headers, title="My Decision")

    audit = (
        db_session.query(AuditLog)
        .filter(AuditLog.user_id == user.id, AuditLog.action == "create", AuditLog.entity_type == "decision", AuditLog.entity_id == did)
        .first()
    )
    assert audit is not None
    assert "My Decision" in audit.description

    ver = (
        db_session.query(DecisionVersion)
        .filter(DecisionVersion.decision_id == did, DecisionVersion.version_number == 1)
        .first()
    )
    assert ver is not None
    assert ver.title == "My Decision"
    assert ver.status == "Draft"


# ============================================================
# 3. UPDATE DECISION — Audit with old/new values + new version
# ============================================================

def test_update_decision_creates_audit_with_old_new_values_and_version(client, db_session, make_token):
    user = _create_user(db_session, "wf_updec@example.com", "EMP_WF_UD")
    headers = _auth_headers(user, make_token)

    did = _create_decision(client, headers, title="Original")

    resp = _update_decision(client, headers, did, title="Revised")
    assert resp.status_code == 200

    audit = (
        db_session.query(AuditLog)
        .filter(AuditLog.user_id == user.id, AuditLog.action == "update", AuditLog.entity_id == did)
        .order_by(AuditLog.id.desc())
        .first()
    )
    assert audit is not None
    assert audit.old_values is not None
    assert audit.new_values is not None

    old = json.loads(audit.old_values)
    new = json.loads(audit.new_values)
    assert old["title"] == "Original"
    assert new["title"] == "Revised"

    versions = (
        db_session.query(DecisionVersion)
        .filter(DecisionVersion.decision_id == did)
        .order_by(DecisionVersion.version_number)
        .all()
    )
    assert len(versions) == 2
    assert versions[0].version_number == 1
    assert versions[1].version_number == 2
    assert versions[1].title == "Original"


# ============================================================
# 4. STATUS CHANGE — Audit + version
# ============================================================

def test_status_change_creates_audit_and_version(client, db_session, make_token):
    user = _create_user(db_session, "wf_statchg@example.com", "EMP_WF_SC")
    headers = _auth_headers(user, make_token)

    did = _create_decision(client, headers)
    resp = _change_status(client, headers, did, "Under Review")
    assert resp.status_code == 200

    audit = (
        db_session.query(AuditLog)
        .filter(AuditLog.user_id == user.id, AuditLog.action == "status_change", AuditLog.entity_id == did)
        .order_by(AuditLog.id.desc())
        .first()
    )
    assert audit is not None
    old = json.loads(audit.old_values)
    new = json.loads(audit.new_values)
    assert old["status"] == "Draft"
    assert new["status"] == "Under Review"

    versions = (
        db_session.query(DecisionVersion)
        .filter(DecisionVersion.decision_id == did)
        .order_by(DecisionVersion.version_number)
        .all()
    )
    assert len(versions) == 2
    assert versions[0].version_number == 1
    assert versions[1].version_number == 2
    assert versions[1].status == "Draft"


# ============================================================
# 5. CREATE ALTERNATIVE — Audit
# ============================================================

def test_create_alternative_creates_audit(client, db_session, make_token):
    user = _create_user(db_session, "wf_alt@example.com", "EMP_WF_ALT")
    headers = _auth_headers(user, make_token)

    did = _create_decision(client, headers)
    resp = _create_alternative(client, headers, did, name="Alternative X")
    assert resp.status_code == 201
    alt_id = resp.json()["id"]

    audit = (
        db_session.query(AuditLog)
        .filter(AuditLog.user_id == user.id, AuditLog.action == "create", AuditLog.entity_type == "alternative", AuditLog.entity_id == alt_id)
        .first()
    )
    assert audit is not None


# ============================================================
# 6. CREATE COMMENT — Audit
# ============================================================

def test_create_comment_creates_audit(client, db_session, make_token):
    user = _create_user(db_session, "wf_cmt@example.com", "EMP_WF_CMT")
    headers = _auth_headers(user, make_token)

    did = _create_decision(client, headers)
    resp = _create_comment(client, headers, did, content="Looks good")
    assert resp.status_code == 201
    cmt_id = resp.json()["id"]

    audit = (
        db_session.query(AuditLog)
        .filter(AuditLog.user_id == user.id, AuditLog.action == "create", AuditLog.entity_type == "comment", AuditLog.entity_id == cmt_id)
        .first()
    )
    assert audit is not None


# ============================================================
# 7. FULL DECISION LIFECYCLE — Draft → Under Review → Approved
# ============================================================

def test_full_lifecycle_audit_and_versions(client, db_session, make_token):
    user = _create_user(db_session, "wf_lifecycle@example.com", "EMP_WF_LC")
    headers = _auth_headers(user, make_token)

    did = _create_decision(client, headers, title="Lifecycle Decision")

    _update_decision(client, headers, did, title="Lifecycle Decision v2")

    _change_status(client, headers, did, "Under Review")

    _change_status(client, headers, did, "Approved")

    audit_actions = (
        db_session.query(AuditLog)
        .filter(AuditLog.user_id == user.id, AuditLog.entity_id == did)
        .order_by(AuditLog.id)
        .all()
    )
    action_types = [a.action for a in audit_actions]
    assert "create" in action_types
    assert "update" in action_types
    assert "status_change" in action_types

    versions = (
        db_session.query(DecisionVersion)
        .filter(DecisionVersion.decision_id == did)
        .order_by(DecisionVersion.version_number)
        .all()
    )
    assert len(versions) == 4
    assert versions[0].version_number == 1
    assert versions[1].version_number == 2
    assert versions[2].version_number == 3
    assert versions[3].version_number == 4
    assert versions[0].status == "Draft"
    assert versions[1].title == "Lifecycle Decision"
    assert versions[2].status == "Draft"
    assert versions[3].status == "Under Review"


# ============================================================
# 8. DECISION HISTORY ENDPOINT
# ============================================================

def test_decision_history_returns_all_audit_entries(client, db_session, make_token):
    user = _create_user(db_session, "wf_hist@example.com", "EMP_WF_HIST")
    headers = _auth_headers(user, make_token)

    did = _create_decision(client, headers, title="Hist Decision")
    _update_decision(client, headers, did, title="Hist Decision v2")
    _change_status(client, headers, did, "Under Review")

    resp = client.get(f"/decisions/{did}/history", headers=headers)
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) >= 3
    entity_ids = [item["entity_id"] for item in items]
    assert all(eid == did for eid in entity_ids)


# ============================================================
# 9. DECISION VERSIONS ENDPOINT
# ============================================================

def test_decision_versions_returns_all_versions(client, db_session, make_token):
    user = _create_user(db_session, "wf_ver@example.com", "EMP_WF_VER")
    headers = _auth_headers(user, make_token)

    did = _create_decision(client, headers)
    _update_decision(client, headers, did)
    _change_status(client, headers, did, "Approved")

    resp = client.get(f"/decisions/{did}/versions", headers=headers)
    assert resp.status_code == 200
    versions = resp.json()["versions"]
    assert len(versions) == 3
    numbers = [v["version_number"] for v in versions]
    assert numbers == sorted(numbers, reverse=True)


def test_get_specific_version(client, db_session, make_token):
    user = _create_user(db_session, "wf_spv@example.com", "EMP_WF_SPV")
    headers = _auth_headers(user, make_token)

    did = _create_decision(client, headers, title="V1 Title")
    _update_decision(client, headers, did, title="V2 Title")

    resp = client.get(f"/decisions/{did}/versions/1", headers=headers)
    assert resp.status_code == 200
    v1 = resp.json()
    assert v1["version_number"] == 1
    assert v1["title"] == "V1 Title"

    resp2 = client.get(f"/decisions/{did}/versions/2", headers=headers)
    assert resp2.status_code == 200
    v2 = resp2.json()
    assert v2["version_number"] == 2
    assert v2["title"] == "V1 Title"


# ============================================================
# 10. ADMIN ACCESS — GET /audit-logs
# ============================================================

def test_admin_can_access_audit_logs_paginated(client, db_session, make_token):
    admin = _create_user(db_session, "wf_adm@example.com", "EMP_WF_ADM", role=UserRole.ADMINISTRATOR)
    user = _create_user(db_session, "wf_aud2@example.com", "EMP_WF_AU2")
    admin_h = _auth_headers(admin, make_token)
    user_h = _auth_headers(user, make_token)

    _create_decision(client, user_h)

    resp = client.get("/audit-logs", headers=admin_h)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    user_ids = {item["user_id"] for item in data["items"]}
    assert user.id in user_ids


# ============================================================
# 11. EMPLOYEE RESTRICTED — /audit-logs (scoping only)
# ============================================================

def test_employee_only_sees_own_audit_logs(client, db_session, make_token):
    emp = _create_user(db_session, "wf_emp@example.com", "EMP_WF_EMP")
    other = _create_user(db_session, "wf_emp2@example.com", "EMP_WF_EMP2")
    emp_h = _auth_headers(emp, make_token)
    other_h = _auth_headers(other, make_token)

    _create_decision(client, emp_h)
    _create_decision(client, other_h)

    resp = client.get("/audit-logs", headers=emp_h)
    assert resp.status_code == 200
    for item in resp.json()["items"]:
        assert item["user_id"] == emp.id


def test_employee_cannot_view_security_logs(client, db_session, make_token):
    emp = _create_user(db_session, "wf_sec_emp@example.com", "EMP_WF_SE")
    emp_h = _auth_headers(emp, make_token)

    resp = client.get("/security/logs", headers=emp_h)
    assert resp.status_code == 403


def test_employee_cannot_view_access_logs(client, db_session, make_token):
    emp = _create_user(db_session, "wf_acc_emp@example.com", "EMP_WF_AE")
    emp_h = _auth_headers(emp, make_token)

    resp = client.get("/access/logs", headers=emp_h)
    assert resp.status_code == 403


# ============================================================
# 12. NO JWT — 401 Unauthorized
# ============================================================

def test_no_jwt_returns_401_on_protected_endpoints(client, db_session, make_token):
    endpoints = [
        ("GET", "/decisions"),
        ("POST", "/decisions"),
        ("GET", "/audit-logs"),
        ("GET", "/security/logs"),
        ("GET", "/access/logs"),
    ]
    for method, path in endpoints:
        if method == "GET":
            resp = client.get(path)
        else:
            resp = client.post(path, json={})
        assert resp.status_code == 401, f"{method} {path} should return 401, got {resp.status_code}"


def test_invalid_jwt_returns_401(client, db_session, make_token):
    resp = client.get(
        "/decisions",
        headers={"Authorization": "Bearer invalid.jwt.token"},
    )
    assert resp.status_code == 401

    sec_logs = (
        db_session.query(SecurityLog)
        .filter(SecurityLog.event_type == "unauthorized_access")
        .all()
    )
    assert len(sec_logs) >= 1
    assert "Invalid or expired JWT" in sec_logs[-1].description


# ============================================================
# 13. ERROR CASES — 404 Not Found
# ============================================================

def test_get_nonexistent_decision_404(client, db_session, make_token):
    user = _create_user(db_session, "wf_404dec@example.com", "EMP_WF_404D")
    headers = _auth_headers(user, make_token)

    resp = client.get("/decisions/999999", headers=headers)
    assert resp.status_code == 404


def test_update_nonexistent_decision_404(client, db_session, make_token):
    user = _create_user(db_session, "wf_404upd@example.com", "EMP_WF_404U")
    headers = _auth_headers(user, make_token)

    resp = client.put("/decisions/999999", json={"title": "X"}, headers=headers)
    assert resp.status_code == 404


def test_status_change_nonexistent_decision_404(client, db_session, make_token):
    user = _create_user(db_session, "wf_404st@example.com", "EMP_WF_404S")
    headers = _auth_headers(user, make_token)

    resp = client.patch("/decisions/999999/status", json={"status": "Approved"}, headers=headers)
    assert resp.status_code == 404


def test_get_nonexistent_version_404(client, db_session, make_token):
    user = _create_user(db_session, "wf_404ver@example.com", "EMP_WF_404V")
    headers = _auth_headers(user, make_token)

    did = _create_decision(client, headers)
    resp = client.get(f"/decisions/{did}/versions/999", headers=headers)
    assert resp.status_code == 404


def test_get_version_of_nonexistent_decision_404(client, db_session, make_token):
    user = _create_user(db_session, "wf_404dver@example.com", "EMP_WF_404DV")
    headers = _auth_headers(user, make_token)

    resp = client.get("/decisions/999999/versions/1", headers=headers)
    assert resp.status_code == 404


# ============================================================
# 14. ERROR CASES — 422 Validation
# ============================================================

def test_invalid_action_filter_422(client, db_session, make_token):
    user = _create_user(db_session, "wf_422act@example.com", "EMP_WF_422A")
    headers = _auth_headers(user, make_token)

    resp = client.get("/audit-logs?action=invalid_action", headers=headers)
    assert resp.status_code == 422


def test_invalid_entity_type_filter_422(client, db_session, make_token):
    user = _create_user(db_session, "wf_422ent@example.com", "EMP_WF_422E")
    headers = _auth_headers(user, make_token)

    resp = client.get("/audit-logs?entity_type=invalid_type", headers=headers)
    assert resp.status_code == 422


def test_invalid_date_format_422(client, db_session, make_token):
    user = _create_user(db_session, "wf_422dt@example.com", "EMP_WF_422D")
    headers = _auth_headers(user, make_token)

    resp = client.get("/audit-logs?start_date=not-a-date", headers=headers)
    assert resp.status_code == 422


def test_reversed_date_range_422(client, db_session, make_token):
    user = _create_user(db_session, "wf_422rev@example.com", "EMP_WF_422R")
    headers = _auth_headers(user, make_token)

    resp = client.get("/audit-logs?start_date=2026-12-31&end_date=2026-01-01", headers=headers)
    assert resp.status_code == 422


def test_invalid_page_size_422(client, db_session, make_token):
    user = _create_user(db_session, "wf_422pg@example.com", "EMP_WF_422P")
    headers = _auth_headers(user, make_token)

    resp = client.get("/audit-logs?page_size=201", headers=headers)
    assert resp.status_code == 422


def test_invalid_page_number_422(client, db_session, make_token):
    user = _create_user(db_session, "wf_422pn@example.com", "EMP_WF_422PN")
    headers = _auth_headers(user, make_token)

    resp = client.get("/audit-logs?page=0", headers=headers)
    assert resp.status_code == 422


def test_invalid_security_event_type_422(client, db_session, make_token):
    admin = _create_user(db_session, "wf_422sec@example.com", "EMP_WF_422S", role=UserRole.ADMINISTRATOR)
    headers = _auth_headers(admin, make_token)

    resp = client.get("/security/logs?event_type=invalid_event", headers=headers)
    assert resp.status_code == 422


# ============================================================
# 15. DB VERIFICATION — Correct IDs, Actions, Timestamps
# ============================================================

def test_audit_log_records_correct_user_action_entity(client, db_session, make_token):
    user = _create_user(db_session, "wf_dbid@example.com", "EMP_WF_DBID")
    headers = _auth_headers(user, make_token)

    did = _create_decision(client, headers, title="DB Verify Decision")

    log = (
        db_session.query(AuditLog)
        .filter(AuditLog.user_id == user.id, AuditLog.action == "create", AuditLog.entity_type == "decision", AuditLog.entity_id == did)
        .first()
    )
    assert log is not None
    assert log.user_id == user.id
    assert log.action == "create"
    assert log.entity_type == "decision"
    assert log.entity_id == did
    assert log.created_at is not None


def test_decision_version_sequential_numbers(client, db_session, make_token):
    user = _create_user(db_session, "wf_seqver@example.com", "EMP_WF_SV")
    headers = _auth_headers(user, make_token)

    did = _create_decision(client, headers)
    _update_decision(client, headers, did)
    _change_status(client, headers, did, "Approved")
    _update_decision(client, headers, did)

    versions = (
        db_session.query(DecisionVersion)
        .filter(DecisionVersion.decision_id == did)
        .order_by(DecisionVersion.version_number)
        .all()
    )
    numbers = [v.version_number for v in versions]
    assert numbers == [1, 2, 3, 4]


def test_security_log_on_forbidden_access(client, db_session, make_token):
    emp = _create_user(db_session, "wf_secforb@example.com", "EMP_WF_SF")
    emp_h = _auth_headers(emp, make_token)

    client.get("/security/logs", headers=emp_h)

    log = (
        db_session.query(SecurityLog)
        .filter(SecurityLog.user_id == emp.id, SecurityLog.event_type == "unauthorized_access")
        .first()
    )
    assert log is not None
    assert "security logs" in log.description.lower()


def test_no_sensitive_data_in_audit_values(client, db_session, make_token):
    user = _create_user(db_session, "wf_nosens@example.com", "EMP_WF_NS")
    headers = _auth_headers(user, make_token)

    did = _create_decision(client, headers)
    _update_decision(client, headers, did, title="Clean Update")

    audit = (
        db_session.query(AuditLog)
        .filter(AuditLog.user_id == user.id, AuditLog.action == "update", AuditLog.entity_id == did)
        .order_by(AuditLog.id.desc())
        .first()
    )
    assert audit is not None
    if audit.new_values:
        vals = json.loads(audit.new_values)
        for key in ["password", "db_password", "token", "api_key", "secret_key", "authorization"]:
            if key in vals:
                assert vals[key] == "***"
