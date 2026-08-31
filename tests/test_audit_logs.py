import json
from datetime import date, datetime, timedelta

from app.models.audit_log import AuditLog
from app.models.enums import UserRole
from app.models.security_log import SecurityLog
from app.models.user import User
from app.core.security import hash_password


def _create_user(db_session, email="audit_pg_user@example.com", employee_id="EMP_APG", role=UserRole.EMPLOYEE):
    user = User(
        full_name="Audit Page User",
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
        json={"title": "Audit Test Decision", "problem_statement": "PS", "category": "Engineering"},
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def _insert_audit_log(db_session, user_id, action="create", entity_type="decision", entity_id=1, created_at=None):
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=f"Test {action} on {entity_type}",
    )
    if created_at:
        entry.created_at = created_at
    db_session.add(entry)
    db_session.commit()
    db_session.refresh(entry)
    return entry


# ============================================================
# GET /audit-logs — Pagination
# ============================================================

def test_audit_logs_page_one(client, db_session, make_token):
    user = _create_user(db_session)
    headers = _auth_headers(user, make_token)

    for i in range(5):
        _create_decision(client, headers)

    resp = client.get("/audit-logs?page=1&page_size=2", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert len(data["items"]) == 2
    assert data["total"] >= 5
    assert data["pages"] >= 3


def test_audit_logs_page_two(client, db_session, make_token):
    user = _create_user(db_session, email="page2@example.com", employee_id="EMP_PG2")
    headers = _auth_headers(user, make_token)

    for i in range(5):
        _create_decision(client, headers)

    resp1 = client.get("/audit-logs?page=1&page_size=2", headers=headers)
    resp2 = client.get("/audit-logs?page=2&page_size=2", headers=headers)
    assert resp1.status_code == 200
    assert resp2.status_code == 200

    ids1 = {item["id"] for item in resp1.json()["items"]}
    ids2 = {item["id"] for item in resp2.json()["items"]}
    assert ids1.isdisjoint(ids2)


def test_audit_logs_empty_page(client, db_session, make_token):
    user = _create_user(db_session, email="empty_pg@example.com", employee_id="EMP_EMPG")
    headers = _auth_headers(user, make_token)

    resp = client.get("/audit-logs?page=999&page_size=10", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["pages"] == 1


def test_audit_logs_default_pagination(client, db_session, make_token):
    user = _create_user(db_session, email="default_pg@example.com", employee_id="EMP_DPG")
    headers = _auth_headers(user, make_token)

    resp = client.get("/audit-logs", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 1
    assert data["page_size"] == 50


def test_audit_logs_page_size_max_200(client, db_session, make_token):
    user = _create_user(db_session, email="max_pg@example.com", employee_id="EMP_MPG")
    headers = _auth_headers(user, make_token)

    resp = client.get("/audit-logs?page_size=201", headers=headers)
    assert resp.status_code == 422


def test_audit_logs_page_must_be_positive(client, db_session, make_token):
    user = _create_user(db_session, email="zero_pg@example.com", employee_id="EMP_ZPG")
    headers = _auth_headers(user, make_token)

    resp = client.get("/audit-logs?page=0", headers=headers)
    assert resp.status_code == 422


# ============================================================
# GET /audit-logs — Filters
# ============================================================

def test_audit_logs_filter_by_user(client, db_session, make_token):
    admin = _create_user(db_session, email="adm_filt@example.com", employee_id="EMP_ADMF", role=UserRole.ADMINISTRATOR)
    user1 = _create_user(db_session, email="u1_filt@example.com", employee_id="EMP_U1F")
    user2 = _create_user(db_session, email="u2_filt@example.com", employee_id="EMP_U2F")

    admin_headers = _auth_headers(admin, make_token)
    u1_headers = _auth_headers(user1, make_token)
    u2_headers = _auth_headers(user2, make_token)

    _create_decision(client, u1_headers)
    _create_decision(client, u2_headers)

    resp = client.get(f"/audit-logs?user={user1.id}", headers=admin_headers)
    assert resp.status_code == 200
    for item in resp.json()["items"]:
        assert item["user_id"] == user1.id


def test_audit_logs_filter_by_action(client, db_session, make_token):
    user = _create_user(db_session, email="act_filt@example.com", employee_id="EMP_AF")
    headers = _auth_headers(user, make_token)
    _create_decision(client, headers)

    resp = client.get("/audit-logs?action=create", headers=headers)
    assert resp.status_code == 200
    for item in resp.json()["items"]:
        assert item["action"] == "create"


def test_audit_logs_filter_by_entity_type(client, db_session, make_token):
    user = _create_user(db_session, email="ent_filt@example.com", employee_id="EMP_EF")
    headers = _auth_headers(user, make_token)
    _create_decision(client, headers)

    resp = client.get("/audit-logs?entity_type=decision", headers=headers)
    assert resp.status_code == 200
    for item in resp.json()["items"]:
        assert item["entity_type"] == "decision"


def test_audit_logs_filter_by_entity_id(client, db_session, make_token):
    user = _create_user(db_session, email="eid_filt@example.com", employee_id="EMP_EID")
    headers = _auth_headers(user, make_token)
    did = _create_decision(client, headers)

    resp = client.get(f"/audit-logs?entity_id={did}", headers=headers)
    assert resp.status_code == 200
    for item in resp.json()["items"]:
        assert item["entity_id"] == did


def test_audit_logs_invalid_action_422(client, db_session, make_token):
    user = _create_user(db_session, email="inv_act@example.com", employee_id="EMP_IA")
    headers = _auth_headers(user, make_token)

    resp = client.get("/audit-logs?action=invalid_action", headers=headers)
    assert resp.status_code == 422


def test_audit_logs_invalid_entity_type_422(client, db_session, make_token):
    user = _create_user(db_session, email="inv_ent@example.com", employee_id="EMP_IE")
    headers = _auth_headers(user, make_token)

    resp = client.get("/audit-logs?entity_type=invalid_type", headers=headers)
    assert resp.status_code == 422


# ============================================================
# GET /audit-logs — Date Filters
# ============================================================

def test_audit_logs_start_date_filter(client, db_session, make_token):
    user = _create_user(db_session, email="sd_filt@example.com", employee_id="EMP_SDF")
    headers = _auth_headers(user, make_token)

    today = date.today().isoformat()
    resp = client.get(f"/audit-logs?start_date={today}", headers=headers)
    assert resp.status_code == 200

    yesterday = (date.today() - timedelta(days=365)).isoformat()
    resp2 = client.get(f"/audit-logs?start_date={yesterday}", headers=headers)
    assert resp2.status_code == 200
    assert resp2.json()["total"] >= resp.json()["total"]


def test_audit_logs_end_date_filter(client, db_session, make_token):
    user = _create_user(db_session, email="ed_filt@example.com", employee_id="EMP_EDF")
    headers = _auth_headers(user, make_token)

    future = (date.today() + timedelta(days=365)).isoformat()
    resp = client.get(f"/audit-logs?end_date={future}", headers=headers)
    assert resp.status_code == 200


def test_audit_logs_date_range_filter(client, db_session, make_token):
    user = _create_user(db_session, email="dr_filt@example.com", employee_id="EMP_DRF")
    headers = _auth_headers(user, make_token)

    today = date.today().isoformat()
    resp = client.get(f"/audit-logs?start_date={today}&end_date={today}", headers=headers)
    assert resp.status_code == 200


def test_audit_logs_invalid_date_format_422(client, db_session, make_token):
    user = _create_user(db_session, email="bad_dt@example.com", employee_id="EMP_BD")
    headers = _auth_headers(user, make_token)

    resp = client.get("/audit-logs?start_date=not-a-date", headers=headers)
    assert resp.status_code == 422
    assert "Invalid date format" in resp.json()["detail"]


def test_audit_logs_invalid_end_date_format_422(client, db_session, make_token):
    user = _create_user(db_session, email="bad_ed@example.com", employee_id="EMP_BDE")
    headers = _auth_headers(user, make_token)

    resp = client.get("/audit-logs?end_date=2026-13-45", headers=headers)
    assert resp.status_code == 422


def test_audit_logs_reversed_date_range_422(client, db_session, make_token):
    user = _create_user(db_session, email="rev_dt@example.com", employee_id="EMP_RD")
    headers = _auth_headers(user, make_token)

    resp = client.get("/audit-logs?start_date=2026-12-31&end_date=2026-01-01", headers=headers)
    assert resp.status_code == 422
    assert "start_date must not be after end_date" in resp.json()["detail"]


# ============================================================
# GET /audit-logs — RBAC
# ============================================================

def test_audit_logs_requires_auth(client, db_session):
    resp = client.get("/audit-logs")
    assert resp.status_code == 401


def test_employee_sees_own_logs_only(client, db_session, make_token):
    emp = _create_user(db_session, email="emp_own@example.com", employee_id="EMP_OWN")
    other = _create_user(db_session, email="other_own@example.com", employee_id="EMP_OTH")

    emp_headers = _auth_headers(emp, make_token)
    other_headers = _auth_headers(other, make_token)

    _create_decision(client, emp_headers)
    _create_decision(client, other_headers)

    resp = client.get("/audit-logs", headers=emp_headers)
    assert resp.status_code == 200
    for item in resp.json()["items"]:
        assert item["user_id"] == emp.id


def test_admin_sees_all_logs(client, db_session, make_token):
    admin = _create_user(db_session, email="admin_all@example.com", employee_id="EMP_AALL", role=UserRole.ADMINISTRATOR)
    user = _create_user(db_session, email="user_all@example.com", employee_id="EMP_UALL")

    admin_headers = _auth_headers(admin, make_token)
    user_headers = _auth_headers(user, make_token)

    _create_decision(client, user_headers)

    resp = client.get("/audit-logs", headers=admin_headers)
    assert resp.status_code == 200
    user_ids = {item["user_id"] for item in resp.json()["items"]}
    assert user.id in user_ids


def test_manager_sees_all_logs(client, db_session, make_token):
    mgr = _create_user(db_session, email="mgr_all@example.com", employee_id="EMP_MALL", role=UserRole.MANAGER)
    user = _create_user(db_session, email="umgr_all@example.com", employee_id="EMP_UMALL")

    mgr_headers = _auth_headers(mgr, make_token)
    user_headers = _auth_headers(user, make_token)

    _create_decision(client, user_headers)

    resp = client.get("/audit-logs", headers=mgr_headers)
    assert resp.status_code == 200
    user_ids = {item["user_id"] for item in resp.json()["items"]}
    assert user.id in user_ids


def test_employee_cannot_filter_other_users(client, db_session, make_token):
    emp = _create_user(db_session, email="emp_nof@example.com", employee_id="EMP_NOF")
    other = _create_user(db_session, email="oth_nof@example.com", employee_id="EMP_ONF")

    emp_headers = _auth_headers(emp, make_token)

    _create_decision(client, emp_headers)

    resp = client.get(f"/audit-logs?user={other.id}", headers=emp_headers)
    assert resp.status_code == 200
    for item in resp.json()["items"]:
        assert item["user_id"] == emp.id


# ============================================================
# GET /audit-logs/{log_id} — RBAC
# ============================================================

def test_audit_logs_get_by_id(client, db_session, make_token):
    user = _create_user(db_session, email="gid@example.com", employee_id="EMP_GID")
    headers = _auth_headers(user, make_token)
    _create_decision(client, headers)

    log = db_session.query(AuditLog).filter(AuditLog.user_id == user.id).first()
    resp = client.get(f"/audit-logs/{log.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == log.id


def test_audit_logs_get_not_found(client, db_session, make_token):
    user = _create_user(db_session, email="gnf@example.com", employee_id="EMP_GNF")
    headers = _auth_headers(user, make_token)

    resp = client.get("/audit-logs/999999", headers=headers)
    assert resp.status_code == 404


def test_employee_cannot_view_other_audit_log(client, db_session, make_token):
    emp1 = _create_user(db_session, email="e1_view@example.com", employee_id="EMP_E1V")
    emp2 = _create_user(db_session, email="e2_view@example.com", employee_id="EMP_E2V")

    emp1_headers = _auth_headers(emp1, make_token)
    emp2_headers = _auth_headers(emp2, make_token)

    _create_decision(client, emp2_headers)

    log = db_session.query(AuditLog).filter(AuditLog.user_id == emp2.id).first()
    resp = client.get(f"/audit-logs/{log.id}", headers=emp1_headers)
    assert resp.status_code == 403


# ============================================================
# Security Logging — Invalid JWT
# ============================================================

def test_invalid_jwt_creates_security_log(client, db_session):
    resp = client.get(
        "/audit-logs",
        headers={"Authorization": "Bearer invalid.jwt.token"},
    )
    assert resp.status_code == 401

    logs = (
        db_session.query(SecurityLog)
        .filter(SecurityLog.event_type == "unauthorized_access")
        .all()
    )
    assert len(logs) >= 1
    latest = logs[-1]
    assert "Invalid or expired JWT token" in latest.description


def test_missing_token_creates_security_log(client, db_session):
    resp = client.get("/audit-logs")
    assert resp.status_code == 401

    logs = (
        db_session.query(SecurityLog)
        .filter(SecurityLog.event_type == "unauthorized_access")
        .all()
    )
    assert len(logs) >= 1
    assert "Missing authentication credentials" in logs[-1].description


# ============================================================
# Security Logging — Forbidden Access
# ============================================================

def test_forbidden_access_logs_security_event(client, db_session, make_token):
    emp = _create_user(db_session, email="forb_emp@example.com", employee_id="EMP_FORB")
    emp_headers = _auth_headers(emp, make_token)

    resp = client.get("/security/logs", headers=emp_headers)
    assert resp.status_code == 403

    logs = (
        db_session.query(SecurityLog)
        .filter(
            SecurityLog.event_type == "unauthorized_access",
            SecurityLog.user_id == emp.id,
        )
        .all()
    )
    assert len(logs) >= 1
    assert "security logs" in logs[-1].description.lower()


def test_forbidden_access_logs_in_access_log_router(client, db_session, make_token):
    emp = _create_user(db_session, email="forb_acc@example.com", employee_id="EMP_FACC")
    emp_headers = _auth_headers(emp, make_token)

    resp = client.get("/access/logs", headers=emp_headers)
    assert resp.status_code == 403

    logs = (
        db_session.query(SecurityLog)
        .filter(
            SecurityLog.event_type == "unauthorized_access",
            SecurityLog.user_id == emp.id,
        )
        .all()
    )
    assert len(logs) >= 1


# ============================================================
# Sensitive Data Sanitization
# ============================================================

def test_password_not_logged_in_audit(client, db_session, make_token):
    user = _create_user(db_session, email="sani_pwd@example.com", employee_id="EMP_SPWD")
    headers = _auth_headers(user, make_token)

    from app.services.audit import log_audit
    log_audit(
        db_session,
        user.id,
        "create",
        "auth",
        description="test sensitive data",
        new_values={"password": "mysecretpassword", "db_password": "dbpass123", "token": "jwt_token_value"},
    )
    db_session.commit()

    log = (
        db_session.query(AuditLog)
        .filter(AuditLog.user_id == user.id, AuditLog.entity_type == "auth")
        .first()
    )
    vals = json.loads(log.new_values)
    assert vals["password"] == "***"
    assert vals["db_password"] == "***"
    assert vals["token"] == "***"


def test_api_key_not_logged(client, db_session, make_token):
    user = _create_user(db_session, email="sani_key@example.com", employee_id="EMP_SKEY")
    headers = _auth_headers(user, make_token)

    from app.services.audit import log_audit
    log_audit(
        db_session,
        user.id,
        "create",
        "auth",
        description="test api key sanitization",
        new_values={"api_key": "sk-12345", "secret_key": "secret123", "authorization": "Bearer xxx"},
    )
    db_session.commit()

    log = (
        db_session.query(AuditLog)
        .filter(AuditLog.user_id == user.id, AuditLog.description == "test api key sanitization")
        .first()
    )
    vals = json.loads(log.new_values)
    assert vals["api_key"] == "***"
    assert vals["secret_key"] == "***"
    assert vals["authorization"] == "***"


def test_non_sensitive_fields_preserved(client, db_session, make_token):
    user = _create_user(db_session, email="sani_vis@example.com", employee_id="EMP_SVIS")

    from app.services.audit import log_audit
    log_audit(
        db_session,
        user.id,
        "create",
        "auth",
        description="test visible fields",
        new_values={"title": "My Decision", "category": "Engineering", "status": "Draft"},
    )
    db_session.commit()

    log = (
        db_session.query(AuditLog)
        .filter(AuditLog.user_id == user.id, AuditLog.description == "test visible fields")
        .first()
    )
    vals = json.loads(log.new_values)
    assert vals["title"] == "My Decision"
    assert vals["category"] == "Engineering"
    assert vals["status"] == "Draft"


# ============================================================
# Audit Records Protection — No PUT/DELETE
# ============================================================

def test_audit_logs_no_put_endpoint(client, db_session, make_token):
    user = _create_user(db_session, email="noput@example.com", employee_id="EMP_NP")
    headers = _auth_headers(user, make_token)

    resp = client.put("/audit-logs", headers=headers)
    assert resp.status_code in (405, 404)


def test_audit_logs_no_delete_endpoint(client, db_session, make_token):
    user = _create_user(db_session, email="nodel@example.com", employee_id="EMP_ND")
    headers = _auth_headers(user, make_token)

    resp = client.delete("/audit-logs", headers=headers)
    assert resp.status_code in (405, 404)


def test_audit_legacy_no_put_endpoint(client, db_session, make_token):
    user = _create_user(db_session, email="nolut@example.com", employee_id="EMP_NLUT")
    headers = _auth_headers(user, make_token)

    resp = client.put("/audit/logs", headers=headers)
    assert resp.status_code in (405, 404)


def test_audit_legacy_no_delete_endpoint(client, db_session, make_token):
    user = _create_user(db_session, email="nold@example.com", employee_id="EMP_NLD")
    headers = _auth_headers(user, make_token)

    resp = client.delete("/audit/logs", headers=headers)
    assert resp.status_code in (405, 404)


# ============================================================
# Security Logs — Date Filters (via /audit-logs with security event types)
# ============================================================

def test_security_log_on_login(client, db_session):
    _create_user(db_session, email="sec_login2@example.com", employee_id="EMP_SL2")

    resp = client.post(
        "/login",
        json={"email": "sec_login2@example.com", "password": "password123"},
    )
    assert resp.status_code == 200

    logs = (
        db_session.query(SecurityLog)
        .filter(SecurityLog.event_type == "login")
        .all()
    )
    assert len(logs) >= 1


def test_security_log_on_failed_login(client, db_session):
    _create_user(db_session, email="sec_fail2@example.com", employee_id="EMP_SF2")

    resp = client.post(
        "/login",
        json={"email": "sec_fail2@example.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 401

    logs = (
        db_session.query(SecurityLog)
        .filter(SecurityLog.event_type == "login_failed")
        .all()
    )
    assert len(logs) >= 1


def test_security_logs_requires_admin_or_manager(client, db_session, make_token):
    emp = _create_user(db_session, email="sec_emp2@example.com", employee_id="EMP_SE2")
    emp_headers = _auth_headers(emp, make_token)

    resp = client.get("/security/logs", headers=emp_headers)
    assert resp.status_code == 403


def test_admin_can_view_security_logs(client, db_session, make_token):
    admin = _create_user(db_session, email="sec_adm2@example.com", employee_id="EMP_SA2", role=UserRole.ADMINISTRATOR)
    admin_headers = _auth_headers(admin, make_token)

    resp = client.get("/security/logs", headers=admin_headers)
    assert resp.status_code == 200


def test_manager_can_view_security_logs(client, db_session, make_token):
    mgr = _create_user(db_session, email="sec_mgr2@example.com", employee_id="EMP_SM2", role=UserRole.MANAGER)
    mgr_headers = _auth_headers(mgr, make_token)

    resp = client.get("/security/logs", headers=mgr_headers)
    assert resp.status_code == 200


def test_security_logs_filter_by_event_type(client, db_session, make_token):
    admin = _create_user(db_session, email="sec_filt2@example.com", employee_id="EMP_SCF2", role=UserRole.ADMINISTRATOR)
    admin_headers = _auth_headers(admin, make_token)

    _create_user(db_session, email="scfilt3@example.com", employee_id="EMP_SCF3")
    client.post("/login", json={"email": "scfilt3@example.com", "password": "password123"})
    client.post("/login", json={"email": "scfilt3@example.com", "password": "wrong"})

    resp = client.get("/security/logs?event_type=login", headers=admin_headers)
    assert resp.status_code == 200
    for log in resp.json():
        assert log["event_type"] == "login"


def test_security_log_invalid_event_type_422(client, db_session, make_token):
    admin = _create_user(db_session, email="sec_inve@example.com", employee_id="EMP_SIE", role=UserRole.ADMINISTRATOR)
    admin_headers = _auth_headers(admin, make_token)

    resp = client.get("/security/logs?event_type=invalid_event", headers=admin_headers)
    assert resp.status_code == 422


def test_security_log_get_by_id(client, db_session, make_token):
    admin = _create_user(db_session, email="sec_get2@example.com", employee_id="EMP_SG2", role=UserRole.ADMINISTRATOR)
    admin_headers = _auth_headers(admin, make_token)

    log = SecurityLog(event_type="login", user_id=admin.id, description="test")
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)

    resp = client.get(f"/security/logs/{log.id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == log.id


def test_security_log_not_found(client, db_session, make_token):
    admin = _create_user(db_session, email="sec_404b@example.com", employee_id="EMP_S404B", role=UserRole.ADMINISTRATOR)
    admin_headers = _auth_headers(admin, make_token)

    resp = client.get("/security/logs/999999", headers=admin_headers)
    assert resp.status_code == 404


# ============================================================
# Access Logs
# ============================================================

def test_access_logs_requires_admin_or_manager(client, db_session, make_token):
    emp = _create_user(db_session, email="acc_emp2@example.com", employee_id="EMP_AE2")
    emp_headers = _auth_headers(emp, make_token)

    resp = client.get("/access/logs", headers=emp_headers)
    assert resp.status_code == 403


def test_admin_can_view_access_logs(client, db_session, make_token):
    admin = _create_user(db_session, email="acc_adm2@example.com", employee_id="EMP_AA2", role=UserRole.ADMINISTRATOR)
    admin_headers = _auth_headers(admin, make_token)

    from app.services.audit import log_access
    log_access(db_session, "GET", "/decisions", 200, user_id=admin.id)
    db_session.commit()

    resp = client.get("/access/logs", headers=admin_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_access_logs_filter_by_method(client, db_session, make_token):
    admin = _create_user(db_session, email="acc_mfil@example.com", employee_id="EMP_AMF", role=UserRole.ADMINISTRATOR)
    admin_headers = _auth_headers(admin, make_token)

    from app.services.audit import log_access
    log_access(db_session, "GET", "/decisions", 200, user_id=admin.id)
    log_access(db_session, "POST", "/decisions", 201, user_id=admin.id)
    db_session.commit()

    resp = client.get("/access/logs?method=GET", headers=admin_headers)
    assert resp.status_code == 200
    for log in resp.json():
        assert log["method"] == "GET"


def test_access_logs_filter_by_status_code(client, db_session, make_token):
    admin = _create_user(db_session, email="acc_sfil@example.com", employee_id="EMPASF", role=UserRole.ADMINISTRATOR)
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
    admin = _create_user(db_session, email="acc_get2@example.com", employee_id="EMP_AG2", role=UserRole.ADMINISTRATOR)
    admin_headers = _auth_headers(admin, make_token)

    from app.services.audit import log_access
    entry = log_access(db_session, "GET", "/test", 200, user_id=admin.id)
    db_session.commit()

    resp = client.get(f"/access/logs/{entry.id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == entry.id


def test_access_log_not_found(client, db_session, make_token):
    admin = _create_user(db_session, email="acc_404b@example.com", employee_id="EMP_A404B", role=UserRole.ADMINISTRATOR)
    admin_headers = _auth_headers(admin, make_token)

    resp = client.get("/access/logs/999999", headers=admin_headers)
    assert resp.status_code == 404


# ============================================================
# Combined: Audit + Security + Access in Full Workflow
# ============================================================

def test_full_workflow_creates_all_log_types(client, db_session, make_token):
    user = _create_user(db_session, email="full_wf2@example.com", employee_id="EMP_FW2")
    headers = _auth_headers(user, make_token)

    decision_id = _create_decision(client, headers)

    client.put(
        f"/decisions/{decision_id}",
        json={"title": "Updated Full WF"},
        headers=headers,
    )
    client.patch(
        f"/decisions/{decision_id}/status",
        json={"status": "Under Review"},
        headers=headers,
    )

    audit_count = (
        db_session.query(AuditLog)
        .filter(AuditLog.user_id == user.id, AuditLog.entity_type == "decision")
        .count()
    )
    assert audit_count >= 3

    resp = client.get("/audit-logs", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total"] >= 3


def test_login_logout_creates_security_logs(client, db_session):
    _create_user(db_session, email="sl_wf@example.com", employee_id="EMP_SLWF")

    resp = client.post("/login", json={"email": "sl_wf@example.com", "password": "password123"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    resp = client.post("/login/logout", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

    sec_logs = (
        db_session.query(SecurityLog)
        .filter(SecurityLog.event_type.in_(["login", "logout"]))
        .all()
    )
    event_types = [l.event_type for l in sec_logs]
    assert "login" in event_types
    assert "logout" in event_types
