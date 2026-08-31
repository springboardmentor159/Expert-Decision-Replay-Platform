import json

from app.models.audit_log import AuditLog
from app.models.decision import Decision
from app.models.decision_version import DecisionVersion
from app.models.enums import UserRole
from app.models.security_log import SecurityLog
from app.models.access_log import AccessLog
from app.models.user import User
from app.core.security import hash_password


def _create_user(db_session, email="audit_user@example.com", employee_id="EMP_AUDIT", role=UserRole.EMPLOYEE):
    user = User(
        full_name="Audit Test User",
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


def _create_decision(client, headers):
    resp = client.post(
        "/decisions",
        json={"title": "Audit Decision", "problem_statement": "PS", "category": "Engineering"},
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


# ============================================================
# Audit Log Tests
# ============================================================

def test_audit_log_created_on_decision_create(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)
    decision_id = _create_decision(client, headers)

    logs = (
        db_session.query(AuditLog)
        .filter(AuditLog.user_id == user.id, AuditLog.entity_type == "decision")
        .all()
    )
    assert any(l.action == "create" and l.entity_id == decision_id for l in logs)


def test_audit_log_created_on_decision_update(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)
    decision_id = _create_decision(client, headers)

    resp = client.put(
        f"/decisions/{decision_id}",
        json={"title": "Updated Audit Decision"},
        headers=headers,
    )
    assert resp.status_code == 200

    logs = (
        db_session.query(AuditLog)
        .filter(AuditLog.user_id == user.id, AuditLog.action == "update")
        .all()
    )
    assert len(logs) >= 1

    log = logs[-1]
    assert log.entity_id == decision_id
    assert log.old_values is not None
    assert log.new_values is not None
    old = json.loads(log.old_values)
    new = json.loads(log.new_values)
    assert old["title"] == "Audit Decision"
    assert new["title"] == "Updated Audit Decision"


def test_audit_log_created_on_status_change(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)
    decision_id = _create_decision(client, headers)

    resp = client.patch(
        f"/decisions/{decision_id}/status",
        json={"status": "Under Review"},
        headers=headers,
    )
    assert resp.status_code == 200

    logs = (
        db_session.query(AuditLog)
        .filter(AuditLog.user_id == user.id, AuditLog.action == "status_change")
        .all()
    )
    assert len(logs) >= 1
    log = logs[-1]
    old = json.loads(log.old_values)
    new = json.loads(log.new_values)
    assert old["status"] == "Draft"
    assert new["status"] == "Under Review"


def test_audit_log_sensitive_fields_sanitized(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)
    decision_id = _create_decision(client, headers)

    from app.services.audit import log_audit
    log_audit(
        db_session,
        user.id,
        "create",
        "auth",
        description="test",
        new_values={"password": "secret123", "token": "abc", "title": "visible"},
    )
    db_session.commit()

    log = (
        db_session.query(AuditLog)
        .filter(AuditLog.user_id == user.id, AuditLog.entity_type == "auth")
        .first()
    )
    vals = json.loads(log.new_values)
    assert vals["password"] == "***"
    assert vals["token"] == "***"
    assert vals["title"] == "visible"


def test_audit_logs_endpoint_requires_auth(client, db_session, make_token):
    resp = client.get("/audit/logs")
    assert resp.status_code == 401


def test_employee_sees_own_audit_logs(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)
    _create_decision(client, headers)

    resp = client.get("/audit/logs", headers=headers)
    assert resp.status_code == 200
    for log in resp.json():
        assert log["user_id"] == user.id


def test_admin_sees_all_audit_logs(client, db_session, make_token):
    admin = _create_user(db_session, email="admin_audit@example.com", employee_id="EMP_ADM_AUDIT", role=UserRole.ADMINISTRATOR)
    user = _create_user(db_session, email="other_audit@example.com", employee_id="EMP_OTH_AUDIT")
    admin_headers = _auth_headers(admin, make_token)
    user_headers = _auth_headers(user, make_token)

    _create_decision(client, user_headers)

    resp = client.get("/audit/logs", headers=admin_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_audit_log_filter_by_action(client, db_session, make_token):
    user = _create_user(db_session, email="filter_audit@example.com", employee_id="EMP_FLT_AUDIT")
    headers = _auth_headers(user, make_token)
    _create_decision(client, headers)

    resp = client.get("/audit/logs?action=create", headers=headers)
    assert resp.status_code == 200
    for log in resp.json():
        assert log["action"] == "create"


def test_audit_log_filter_by_entity_type(client, db_session, make_token):
    user = _create_user(db_session, email="filter_ent_audit@example.com", employee_id="EMP_FEN_AUDIT")
    headers = _auth_headers(user, make_token)
    _create_decision(client, headers)

    resp = client.get("/audit/logs?entity_type=decision", headers=headers)
    assert resp.status_code == 200
    for log in resp.json():
        assert log["entity_type"] == "decision"


def test_audit_log_get_by_id(client, db_session, make_token):
    user = _create_user(db_session, email="get_audit@example.com", employee_id="EMP_GEA_AUDIT")
    headers = _auth_headers(user, make_token)
    _create_decision(client, headers)

    log = (
        db_session.query(AuditLog)
        .filter(AuditLog.user_id == user.id)
        .first()
    )
    resp = client.get(f"/audit/logs/{log.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == log.id


def test_audit_log_get_not_found(client, db_session, make_token):
    user = _create_user(db_session, email="nf_audit@example.com", employee_id="EMP_NFA_AUDIT")
    headers = _auth_headers(user, make_token)
    resp = client.get("/audit/logs/999999", headers=headers)
    assert resp.status_code == 404


def test_audit_log_invalid_action_rejected(client, db_session, make_token):
    user = _create_user(db_session, email="inv_audit@example.com", employee_id="EMP_INVA_AUDIT")
    headers = _auth_headers(user, make_token)
    resp = client.get("/audit/logs?action=invalid_action", headers=headers)
    assert resp.status_code == 422


def test_audit_log_invalid_entity_type_rejected(client, db_session, make_token):
    user = _create_user(db_session, email="inent_audit@example.com", employee_id="EMP_INENT_AUDIT")
    headers = _auth_headers(user, make_token)
    resp = client.get("/audit/logs?entity_type=invalid_type", headers=headers)
    assert resp.status_code == 422


# ============================================================
# Decision Version Tests
# ============================================================

def test_decision_version_created_on_update(client, db_session, make_token):
    user = _create_user(db_session, email="ver_upd@example.com", employee_id="EMP_VERUPD")
    headers = _auth_headers(user, make_token)
    decision_id = _create_decision(client, headers)

    client.put(
        f"/decisions/{decision_id}",
        json={"title": "Versioned Decision"},
        headers=headers,
    )

    versions = (
        db_session.query(DecisionVersion)
        .filter(DecisionVersion.decision_id == decision_id)
        .order_by(DecisionVersion.version_number)
        .all()
    )
    assert len(versions) >= 1
    assert versions[0].title == "Audit Decision"
    assert versions[0].version_number == 1


def test_decision_version_created_on_status_change(client, db_session, make_token):
    user = _create_user(db_session, email="ver_stat@example.com", employee_id="EMP_VERSTAT")
    headers = _auth_headers(user, make_token)
    decision_id = _create_decision(client, headers)

    client.patch(
        f"/decisions/{decision_id}/status",
        json={"status": "Approved"},
        headers=headers,
    )

    versions = (
        db_session.query(DecisionVersion)
        .filter(DecisionVersion.decision_id == decision_id)
        .order_by(DecisionVersion.version_number)
        .all()
    )
    assert len(versions) >= 1
    assert versions[0].status == "Draft"


def test_decision_version_sequential_numbering(client, db_session, make_token):
    user = _create_user(db_session, email="ver_seq@example.com", employee_id="EMP_VERSEQ")
    headers = _auth_headers(user, make_token)
    decision_id = _create_decision(client, headers)

    client.put(
        f"/decisions/{decision_id}",
        json={"title": "V2"},
        headers=headers,
    )
    client.patch(
        f"/decisions/{decision_id}/status",
        json={"status": "Under Review"},
        headers=headers,
    )

    versions = (
        db_session.query(DecisionVersion)
        .filter(DecisionVersion.decision_id == decision_id)
        .order_by(DecisionVersion.version_number)
        .all()
    )
    assert len(versions) >= 2
    assert versions[0].version_number == 1
    assert versions[1].version_number == 2


def test_decision_version_endpoint_list(client, db_session, make_token):
    user = _create_user(db_session, email="ver_list@example.com", employee_id="EMP_VERLST")
    headers = _auth_headers(user, make_token)
    decision_id = _create_decision(client, headers)

    client.put(
        f"/decisions/{decision_id}",
        json={"title": "Updated"},
        headers=headers,
    )

    resp = client.get(f"/decisions/{decision_id}/versions", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "versions" in data
    assert len(data["versions"]) >= 1
    assert data["versions"][0]["decision_id"] == decision_id


def test_decision_version_not_found(client, db_session, make_token):
    user = _create_user(db_session, email="ver_404@example.com", employee_id="EMP_VER404")
    headers = _auth_headers(user, make_token)
    resp = client.get("/decisions/999999/versions", headers=headers)
    assert resp.status_code == 404


def test_decision_version_get_by_number(client, db_session, make_token):
    user = _create_user(db_session, email="ver_gbn@example.com", employee_id="EMP_VERGBN")
    headers = _auth_headers(user, make_token)
    decision_id = _create_decision(client, headers)

    client.put(
        f"/decisions/{decision_id}",
        json={"title": "V2"},
        headers=headers,
    )

    resp = client.get(f"/decisions/{decision_id}/versions/1", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["version_number"] == 1


def test_decision_version_get_not_found(client, db_session, make_token):
    user = _create_user(db_session, email="ver_gnf@example.com", employee_id="EMPVERGNF")
    headers = _auth_headers(user, make_token)
    decision_id = _create_decision(client, headers)
    resp = client.get(f"/decisions/{decision_id}/versions/999", headers=headers)
    assert resp.status_code == 404


def test_decision_version_requires_auth(client, db_session, make_token):
    resp = client.get("/decisions/1/versions")
    assert resp.status_code == 401


def test_decision_version_snapshot_has_rationale(client, db_session, make_token):
    user = _create_user(db_session, email="ver_rat@example.com", employee_id="EMPVERRAT")
    headers = _auth_headers(user, make_token)
    decision_id = _create_decision(client, headers)

    client.put(
        f"/decisions/{decision_id}/rationale",
        json={"rationale": "Important rationale"},
        headers=headers,
    )

    versions = (
        db_session.query(DecisionVersion)
        .filter(DecisionVersion.decision_id == decision_id)
        .order_by(DecisionVersion.version_number)
        .all()
    )
    versions_with_rationale = [v for v in versions if v.rationale]
    assert len(versions_with_rationale) >= 1


# ============================================================
# Security Log Tests
# ============================================================

def test_security_log_on_login(client, db_session, make_token):
    user = _create_user(db_session, email="sec_login@example.com", employee_id="EMP_SECLOGIN")

    resp = client.post(
        "/login",
        json={"email": "sec_login@example.com", "password": "password123"},
    )
    assert resp.status_code == 200

    logs = (
        db_session.query(SecurityLog)
        .filter(SecurityLog.user_id == user.id, SecurityLog.event_type == "login")
        .all()
    )
    assert len(logs) >= 1


def test_security_log_on_failed_login(client, db_session, make_token):
    resp = client.post(
        "/login",
        json={"email": "nonexistent@example.com", "password": "wrongpass"},
    )
    assert resp.status_code == 401

    logs = (
        db_session.query(SecurityLog)
        .filter(SecurityLog.event_type == "login_failed")
        .all()
    )
    assert len(logs) >= 1


def test_security_logs_endpoint_requires_admin(client, db_session, make_token):
    emp = _create_user(db_session, email="sec_emp@example.com", employee_id="EMP_SEC1")
    emp_headers = _auth_headers(emp, make_token)

    resp = client.get("/security/logs", headers=emp_headers)
    assert resp.status_code == 403


def test_admin_can_view_security_logs(client, db_session, make_token):
    admin = _create_user(db_session, email="sec_admin@example.com", employee_id="EMP_SECADM", role=UserRole.ADMINISTRATOR)
    admin_headers = _auth_headers(admin, make_token)

    resp = client.get("/security/logs", headers=admin_headers)
    assert resp.status_code == 200


def test_security_logs_requires_auth(client, db_session):
    resp = client.get("/security/logs")
    assert resp.status_code == 401


def test_security_log_filter_by_event_type(client, db_session, make_token):
    admin = _create_user(db_session, email="sec_filt@example.com", employee_id="EMP_SECFILT", role=UserRole.ADMINISTRATOR)
    admin_headers = _auth_headers(admin, make_token)

    _create_user(db_session, email="secfilt2@example.com", employee_id="EMP_SECFILT2")

    client.post("/login", json={"email": "secfilt2@example.com", "password": "password123"})
    client.post("/login", json={"email": "secfilt2@example.com", "password": "wrong"})

    resp = client.get("/security/logs?event_type=login", headers=admin_headers)
    assert resp.status_code == 200
    for log in resp.json():
        assert log["event_type"] == "login"


def test_security_log_get_by_id(client, db_session, make_token):
    admin = _create_user(db_session, email="sec_get@example.com", employee_id="EMP_SECGET", role=UserRole.ADMINISTRATOR)
    admin_headers = _auth_headers(admin, make_token)

    log = SecurityLog(
        event_type="login",
        user_id=admin.id,
        description="test",
    )
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)

    resp = client.get(f"/security/logs/{log.id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == log.id


def test_security_log_not_found(client, db_session, make_token):
    admin = _create_user(db_session, email="sec_404@example.com", employee_id="EMP_SEC404", role=UserRole.ADMINISTRATOR)
    admin_headers = _auth_headers(admin, make_token)

    resp = client.get("/security/logs/999999", headers=admin_headers)
    assert resp.status_code == 404


def test_security_log_event_type_sanitized(client, db_session, make_token):
    admin = _create_user(db_session, email="sec_sani@example.com", employee_id="EMP_SECSANI", role=UserRole.ADMINISTRATOR)
    admin_headers = _auth_headers(admin, make_token)

    resp = client.get("/security/logs?event_type=invalid_event", headers=admin_headers)
    assert resp.status_code == 422


# ============================================================
# Access Log Tests
# ============================================================

def test_access_logs_endpoint_requires_admin(client, db_session, make_token):
    emp = _create_user(db_session, email="acc_emp@example.com", employee_id="EMP_ACC1")
    emp_headers = _auth_headers(emp, make_token)

    resp = client.get("/access/logs", headers=emp_headers)
    assert resp.status_code == 403


def test_admin_can_view_access_logs(client, db_session, make_token):
    admin = _create_user(db_session, email="acc_admin@example.com", employee_id="EMP_ACCADM", role=UserRole.ADMINISTRATOR)
    admin_headers = _auth_headers(admin, make_token)

    from app.services.audit import log_access
    log_access(db_session, "GET", "/decisions", 200, user_id=admin.id)
    db_session.commit()

    resp = client.get("/access/logs", headers=admin_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_access_logs_requires_auth(client, db_session):
    resp = client.get("/access/logs")
    assert resp.status_code == 401


def test_access_log_filter_by_method(client, db_session, make_token):
    admin = _create_user(db_session, email="acc_filt@example.com", employee_id="EMP_ACCFILT", role=UserRole.ADMINISTRATOR)
    admin_headers = _auth_headers(admin, make_token)

    from app.services.audit import log_access
    log_access(db_session, "GET", "/decisions", 200, user_id=admin.id)
    log_access(db_session, "POST", "/decisions", 201, user_id=admin.id)
    db_session.commit()

    resp = client.get("/access/logs?method=GET", headers=admin_headers)
    assert resp.status_code == 200
    for log in resp.json():
        assert log["method"] == "GET"


def test_access_log_filter_by_status_code(client, db_session, make_token):
    admin = _create_user(db_session, email="acc_stc@example.com", employee_id="EMP_ACCSTC", role=UserRole.ADMINISTRATOR)
    admin_headers = _auth_headers(admin, make_token)

    from app.services.audit import log_access
    log_access(db_session, "GET", "/decisions", 200, user_id=admin.id)
    log_access(db_session, "GET", "/invalid", 404, user_id=admin.id)
    db_session.commit()

    resp = client.get("/access/logs?status_code=200", headers=admin_headers)
    assert resp.status_code == 200
    for log in resp.json():
        assert log["status_code"] == 200


def test_access_log_get_by_id(client, db_session, make_token):
    admin = _create_user(db_session, email="acc_get@example.com", employee_id="EMP_ACCGET", role=UserRole.ADMINISTRATOR)
    admin_headers = _auth_headers(admin, make_token)

    from app.services.audit import log_access
    entry = log_access(db_session, "GET", "/test", 200, user_id=admin.id)
    db_session.commit()

    resp = client.get(f"/access/logs/{entry.id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == entry.id


def test_access_log_not_found(client, db_session, make_token):
    admin = _create_user(db_session, email="acc_404@example.com", employee_id="EMP_ACC404", role=UserRole.ADMINISTRATOR)
    admin_headers = _auth_headers(admin, make_token)

    resp = client.get("/access/logs/999999", headers=admin_headers)
    assert resp.status_code == 404


# ============================================================
# Integration: audit + version on full workflow
# ============================================================

def test_full_decision_workflow_creates_audit_and_versions(client, db_session, make_token):
    user = _create_user(db_session, email="full_wf@example.com", employee_id="EMP_FULLWF")
    headers = _auth_headers(user, make_token)

    decision_id = _create_decision(client, headers)
    client.put(
        f"/decisions/{decision_id}",
        json={"title": "Updated Title"},
        headers=headers,
    )
    client.patch(
        f"/decisions/{decision_id}/status",
        json={"status": "Approved"},
        headers=headers,
    )

    audit_count = (
        db_session.query(AuditLog)
        .filter(
            AuditLog.user_id == user.id,
            AuditLog.entity_type == "decision",
        )
        .count()
    )
    assert audit_count >= 3

    version_count = (
        db_session.query(DecisionVersion)
        .filter(DecisionVersion.decision_id == decision_id)
        .count()
    )
    assert version_count >= 2
