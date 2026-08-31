from app.models.decision import Decision
from app.models.enums import UserRole
from app.models.user import User
from app.core.security import hash_password


def _create_user(db_session, email, employee_id, role=UserRole.EMPLOYEE):
    user = User(
        full_name="Dashboard Test User",
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
    return {"Authorization": f"Bearer {make_token(str(user.id))}"}


def _create_decision(client, headers, status_value="Draft"):
    return client.post(
        "/decisions",
        json={"title": "D", "problem_statement": "PS", "category": "Engineering"},
        headers=headers,
    )


def test_employee_dashboard_own_stats_only(client, db_session, make_token):
    emp_a = _create_user(db_session, "dash_a@example.com", "EMP_DA", UserRole.EMPLOYEE)
    emp_b = _create_user(db_session, "dash_b@example.com", "EMP_DB", UserRole.EMPLOYEE)
    headers_a = _auth_headers(emp_a, make_token)
    headers_b = _auth_headers(emp_b, make_token)

    # 2 Draft + 1 Approved for A
    _create_decision(client, headers_a)
    _create_decision(client, headers_a)
    d3 = _create_decision(client, headers_a).json()["id"]
    client.patch(f"/decisions/{d3}/status", json={"status": "Approved"}, headers=headers_a)

    # 1 decision for B (should NOT appear in A's dashboard)
    _create_decision(client, headers_b)

    res = client.get("/dashboard/employee", headers=headers_a)
    assert res.status_code == 200
    body = res.json()
    assert body["user_id"] == emp_a.id
    assert body["total_decisions"] == 3

    by_status = {s["status"]: s["count"] for s in body["decisions_by_status"]}
    assert by_status["Draft"] == 2
    assert by_status["Approved"] == 1
    assert by_status["Under Review"] == 0
    assert by_status["Rejected"] == 0
    assert by_status["Archived"] == 0

    # B's dashboard must only show B's own single decision
    res_b = client.get("/dashboard/employee", headers=headers_b)
    assert res_b.json()["total_decisions"] == 1


def test_employee_dashboard_recent_activity(client, db_session, make_token):
    emp = _create_user(db_session, "dash_act@example.com", "EMP_DACT")
    headers = _auth_headers(emp, make_token)
    _create_decision(client, headers)

    res = client.get("/dashboard/employee", headers=headers)
    assert res.status_code == 200
    activity = res.json()["recent_activity"]
    assert len(activity) >= 1
    assert any(a["action"] == "create" and a["entity_type"] == "decision" for a in activity)


def test_employee_dashboard_changes_after_actions(client, db_session, make_token):
    emp = _create_user(db_session, "dash_chg@example.com", "EMP_DCHG")
    headers = _auth_headers(emp, make_token)

    before = client.get("/dashboard/employee", headers=headers).json()["total_decisions"]
    assert before == 0

    d_id = _create_decision(client, headers).json()["id"]
    alt = client.post(
        f"/decisions/{d_id}/alternatives",
        json={"name": "A", "description": "d", "pros": "p", "cons": "c"},
        headers=headers,
    ).json()["id"]
    client.post(f"/decisions/{d_id}/comments", json={"content": "c"}, headers=headers)

    after = client.get("/dashboard/employee", headers=headers).json()
    assert after["total_decisions"] == 1
    # recent activity should reflect the create/update/comment actions
    actions = {(a["action"], a["entity_type"]) for a in after["recent_activity"]}
    assert ("create", "decision") in actions
    assert ("create", "alternative") in actions
    assert ("create", "comment") in actions


def test_manager_statistics_counts_match(client, db_session, make_token):
    emp = _create_user(db_session, "dash_m_emp@example.com", "EMP_DME")
    mgr = _create_user(db_session, "dash_m_mgr@example.com", "EMP_DMM", UserRole.MANAGER)
    headers_emp = _auth_headers(emp, make_token)
    headers_mgr = _auth_headers(mgr, make_token)

    # Build a known org-wide distribution
    ids = [_create_decision(client, headers_emp).json()["id"] for _ in range(4)]
    client.patch(f"/decisions/{ids[0]}/status", json={"status": "Approved"}, headers=headers_emp)
    client.patch(f"/decisions/{ids[1]}/status", json={"status": "Under Review"}, headers=headers_emp)
    client.patch(f"/decisions/{ids[2]}/status", json={"status": "Rejected"}, headers=headers_emp)
    client.patch(f"/decisions/{ids[3]}/status", json={"status": "Archived"}, headers=headers_emp)

    res = client.get("/dashboard/manager/statistics", headers=headers_mgr)
    assert res.status_code == 200
    stats = res.json()
    assert stats["scope"] == "org-wide"
    assert stats["total"] == 4
    assert stats["draft"] == 0
    assert stats["approved"] == 1
    assert stats["under_review"] == 1
    assert stats["rejected"] == 1
    assert stats["archived"] == 1


def test_employee_blocked_from_manager_statistics(client, db_session, make_token):
    emp = _create_user(db_session, "dash_403@example.com", "EMP_D403")
    headers = _auth_headers(emp, make_token)

    res = client.get("/dashboard/manager/statistics", headers=headers)
    assert res.status_code == 403
    assert res.json()["detail"] == "Not authorized to view manager dashboards"


def test_manager_pending_approvals_blocked_501(client, db_session, make_token):
    mgr = _create_user(db_session, "dash_p_mgr@example.com", "EMP_DPM", UserRole.MANAGER)
    headers = _auth_headers(mgr, make_token)

    res = client.get("/dashboard/manager/pending-approvals", headers=headers)
    assert res.status_code == 501
    assert "approval workflow" in res.json()["detail"].lower()


def test_employee_pending_approvals_403(client, db_session, make_token):
    emp = _create_user(db_session, "dash_p_emp@example.com", "EMP_DPE", UserRole.EMPLOYEE)
    headers = _auth_headers(emp, make_token)

    res = client.get("/dashboard/manager/pending-approvals", headers=headers)
    assert res.status_code == 403


def test_dashboard_endpoints_require_token(client):
    for url in ["/dashboard/employee", "/dashboard/manager/statistics", "/dashboard/manager/pending-approvals"]:
        res = client.get(url)
        assert res.status_code == 401
        assert res.json()["detail"] == "Not authenticated"


def test_admin_dashboard_requires_admin_role(client, db_session, make_token):
    emp = _create_user(db_session, "dash_adm_emp@example.com", "EMP_DAE", UserRole.EMPLOYEE)
    mgr = _create_user(db_session, "dash_adm_mgr@example.com", "EMP_DAM", UserRole.MANAGER)
    adm = _create_user(db_session, "dash_adm_adm@example.com", "EMP_DAA", UserRole.ADMINISTRATOR)
    headers_emp = _auth_headers(emp, make_token)
    headers_mgr = _auth_headers(mgr, make_token)
    headers_adm = _auth_headers(adm, make_token)

    res = client.get("/dashboard/admin", headers=headers_emp)
    assert res.status_code == 403
    assert res.json()["detail"] == "Not authorized to view admin dashboards"

    res = client.get("/dashboard/admin", headers=headers_mgr)
    assert res.status_code == 403

    res = client.get("/dashboard/admin", headers=headers_adm)
    assert res.status_code == 200
    body = res.json()
    assert "total_users" in body
    assert "total_decisions" in body
    assert "decision_stats" in body
    assert "approval_stats" in body
    assert "recent_activity" in body
    # approval_stats should be None since workflow not implemented
    assert body["approval_stats"] is None


def test_admin_analytics_requires_admin_role(client, db_session, make_token):
    emp = _create_user(db_session, "dash_an_emp@example.com", "EMP_DANE", UserRole.EMPLOYEE)
    mgr = _create_user(db_session, "dash_an_mgr@example.com", "EMP_DANM", UserRole.MANAGER)
    adm = _create_user(db_session, "dash_an_adm@example.com", "EMP_DANA", UserRole.ADMINISTRATOR)
    headers_emp = _auth_headers(emp, make_token)
    headers_mgr = _auth_headers(mgr, make_token)
    headers_adm = _auth_headers(adm, make_token)

    res = client.get("/dashboard/admin/analytics", headers=headers_emp)
    assert res.status_code == 403

    res = client.get("/dashboard/admin/analytics", headers=headers_mgr)
    assert res.status_code == 403

    res = client.get("/dashboard/admin/analytics", headers=headers_adm)
    assert res.status_code == 200
    body = res.json()
    assert "decision_stats" in body
    assert "user_stats" in body
    assert "approval_stats" in body
    assert body["approval_stats"] is None

    # Verify user_stats structure
    user_stats = body["user_stats"]
    assert "total" in user_stats
    assert "active" in user_stats
    assert "by_role" in user_stats
    assert isinstance(user_stats["by_role"], list)
    for role_count in user_stats["by_role"]:
        assert "role" in role_count
        assert "count" in role_count


def test_admin_decision_activity_requires_admin_role(client, db_session, make_token):
    emp = _create_user(db_session, "dash_da_emp@example.com", "EMP_DDAE", UserRole.EMPLOYEE)
    mgr = _create_user(db_session, "dash_da_mgr@example.com", "EMP_DDAM", UserRole.MANAGER)
    adm = _create_user(db_session, "dash_da_adm@example.com", "EMP_DDAA", UserRole.ADMINISTRATOR)
    headers_emp = _auth_headers(emp, make_token)
    headers_mgr = _auth_headers(mgr, make_token)
    headers_adm = _auth_headers(adm, make_token)

    res = client.get("/dashboard/admin/decision-activity", headers=headers_emp)
    assert res.status_code == 403

    res = client.get("/dashboard/admin/decision-activity", headers=headers_mgr)
    assert res.status_code == 403

    res = client.get("/dashboard/admin/decision-activity", headers=headers_adm)
    assert res.status_code == 200
    body = res.json()
    assert "granularity" in body
    assert "data" in body
    assert isinstance(body["data"], list)


def test_admin_decision_activity_granularity_options(client, db_session, make_token):
    adm = _create_user(db_session, "dash_da2_adm@example.com", "EMP_DDA2", UserRole.ADMINISTRATOR)
    headers_adm = _auth_headers(adm, make_token)

    for gran in ["day", "week", "month"]:
        res = client.get(f"/dashboard/admin/decision-activity?granularity={gran}", headers=headers_adm)
        assert res.status_code == 200
        body = res.json()
        assert body["granularity"] == gran
        assert isinstance(body["data"], list)


def test_admin_dashboard_endpoints_require_token(client):
    for url in ["/dashboard/admin", "/dashboard/admin/analytics", "/dashboard/admin/decision-activity"]:
        res = client.get(url)
        assert res.status_code == 401
        assert res.json()["detail"] == "Not authenticated"


def test_admin_dashboard_decision_stats_match_sql(client, db_session, make_token):
    """Verify admin dashboard decision stats match direct SQL GROUP BY."""
    adm = _create_user(db_session, "dash_sql_adm@example.com", "EMP_DSQL", UserRole.ADMINISTRATOR)
    emp = _create_user(db_session, "dash_sql_emp@example.com", "EMP_DSQLE", UserRole.EMPLOYEE)
    headers_adm = _auth_headers(adm, make_token)
    headers_emp = _auth_headers(emp, make_token)

    # Create decisions with various statuses
    ids = [_create_decision(client, headers_emp).json()["id"] for _ in range(5)]
    client.patch(f"/decisions/{ids[0]}/status", json={"status": "Approved"}, headers=headers_emp)
    client.patch(f"/decisions/{ids[1]}/status", json={"status": "Under Review"}, headers=headers_emp)
    client.patch(f"/decisions/{ids[2]}/status", json={"status": "Rejected"}, headers=headers_emp)
    client.patch(f"/decisions/{ids[3]}/status", json={"status": "Archived"}, headers=headers_emp)
    # ids[4] stays Draft

    res = client.get("/dashboard/admin", headers=headers_adm)
    assert res.status_code == 200
    stats = res.json()["decision_stats"]

    # Verify against SQL
    from sqlalchemy import func
    from app.models.decision import Decision
    from app.models.enums import DecisionStatus

    rows = db_session.query(Decision.status, func.count(Decision.id)).group_by(Decision.status).all()
    counts = {s.value: 0 for s in DecisionStatus}
    for status_value, count in rows:
        key = status_value.value if hasattr(status_value, "value") else str(status_value)
        if key in counts:
            counts[key] = count

    assert stats["total"] == sum(counts.values())
    assert stats["draft"] == counts[DecisionStatus.DRAFT.value]
    assert stats["under_review"] == counts[DecisionStatus.UNDER_REVIEW.value]
    assert stats["approved"] == counts[DecisionStatus.APPROVED.value]
    assert stats["rejected"] == counts[DecisionStatus.REJECTED.value]
    assert stats["archived"] == counts[DecisionStatus.ARCHIVED.value]


# ── Part D: Admin Approval Statistics (BLOCKED) ──────────────────────────────

def test_admin_approval_statistics_blocked_501(client, db_session, make_token):
    admin = _create_user(db_session, "dash_admin@approve.com", "EMP_DAPR", UserRole.ADMINISTRATOR)
    headers = _auth_headers(admin, make_token)

    res = client.get("/dashboard/admin/approval-statistics", headers=headers)
    assert res.status_code == 501
    assert "approval workflow" in res.json()["detail"].lower()


def test_employee_blocked_from_approval_statistics(client, db_session, make_token):
    emp = _create_user(db_session, "dash_as_emp@example.com", "EMP_DASE")
    headers = _auth_headers(emp, make_token)

    res = client.get("/dashboard/admin/approval-statistics", headers=headers)
    assert res.status_code == 403
    assert res.json()["detail"] == "Not authorized to view admin dashboards"


# ── Part D: Admin User Activity ──────────────────────────────────────────────

def test_admin_user_activity_shows_active_users(client, db_session, make_token):
    admin = _create_user(db_session, "dash_ua_admin@example.com", "EMP_DUA", UserRole.ADMINISTRATOR)
    emp = _create_user(db_session, "dash_ua_emp@example.com", "EMP_DUAE")
    headers_admin = _auth_headers(admin, make_token)
    headers_emp = _auth_headers(emp, make_token)

    # Emp creates decisions + comment (generates activity)
    _create_decision(client, headers_emp)
    d_id = _create_decision(client, headers_emp).json()["id"]
    client.post(f"/decisions/{d_id}/comments", json={"content": "c"}, headers=headers_emp)

    # Admin creates one decision
    _create_decision(client, headers_admin)

    res = client.get("/dashboard/admin/user-activity", headers=headers_admin)
    assert res.status_code == 200
    body = res.json()
    assert body["total_active_users"] >= 2

    # Find the employee and admin in the list
    user_ids = {u["user_id"]: u for u in body["users"]}
    assert emp.id in user_ids
    assert admin.id in user_ids

    emp_data = user_ids[emp.id]
    assert emp_data["total_actions"] >= 3  # 2 create decisions + 1 create comment
    assert "create:decision" in emp_data["actions_by_type"]
    assert "create:comment" in emp_data["actions_by_type"]


def test_admin_user_activity_date_filter(client, db_session, make_token):
    admin = _create_user(db_session, "dash_ua_date@example.com", "EMP_DUAD", UserRole.ADMINISTRATOR)
    headers = _auth_headers(admin, make_token)

    _create_decision(client, headers)

    # Use today's date - should find the activity
    from datetime import date
    today = date.today().isoformat()
    res = client.get(f"/dashboard/admin/user-activity?start_date={today}", headers=headers)
    assert res.status_code == 200
    assert res.json()["total_active_users"] >= 1

    # Use a future date - should find nothing
    res = client.get("/dashboard/admin/user-activity?start_date=2099-01-01", headers=headers)
    assert res.status_code == 200
    assert res.json()["total_active_users"] == 0


def test_employee_blocked_from_user_activity(client, db_session, make_token):
    emp = _create_user(db_session, "dash_ua_emp2@example.com", "EMP_DUAE2")
    headers = _auth_headers(emp, make_token)

    res = client.get("/dashboard/admin/user-activity", headers=headers)
    assert res.status_code == 403


# ── Part D: Activities Endpoint ──────────────────────────────────────────────

def test_activities_admin_sees_all(client, db_session, make_token):
    admin = _create_user(db_session, "act_admin@example.com", "EMP_ACA", UserRole.ADMINISTRATOR)
    emp_a = _create_user(db_session, "act_emp_a@example.com", "EMP_AEA")
    emp_b = _create_user(db_session, "act_emp_b@example.com", "EMP_AEB")
    headers_admin = _auth_headers(admin, make_token)
    headers_a = _auth_headers(emp_a, make_token)
    headers_b = _auth_headers(emp_b, make_token)

    _create_decision(client, headers_a)
    _create_decision(client, headers_b)
    _create_decision(client, headers_admin)

    res = client.get("/activities", headers=headers_admin)
    assert res.status_code == 200
    body = res.json()
    assert body["total"] >= 3
    user_ids = {item["user_id"] for item in body["items"]}
    assert emp_a.id in user_ids
    assert emp_b.id in user_ids
    assert admin.id in user_ids


def test_activities_non_admin_sees_own_only(client, db_session, make_token):
    emp_a = _create_user(db_session, "act_own_a@example.com", "EMP_AOA")
    emp_b = _create_user(db_session, "act_own_b@example.com", "EMP_AOB")
    headers_a = _auth_headers(emp_a, make_token)
    headers_b = _auth_headers(emp_b, make_token)

    _create_decision(client, headers_a)
    _create_decision(client, headers_b)

    res_a = client.get("/activities", headers=headers_a)
    assert res_a.status_code == 200
    body_a = res_a.json()
    assert body_a["total"] == 1
    assert body_a["items"][0]["user_id"] == emp_a.id

    res_b = client.get("/activities", headers=headers_b)
    assert res_b.status_code == 200
    assert res_b.json()["total"] == 1
    assert res_b.json()["items"][0]["user_id"] == emp_b.id


def test_activities_filter_by_action(client, db_session, make_token):
    emp = _create_user(db_session, "act_f_action@example.com", "EMP_AFA")
    headers = _auth_headers(emp, make_token)

    d_id = _create_decision(client, headers).json()["id"]
    client.patch(f"/decisions/{d_id}/status", json={"status": "Under Review"}, headers=headers)

    res = client.get("/activities?action=create", headers=headers)
    assert res.status_code == 200
    assert all(item["action"] == "create" for item in res.json()["items"])

    res = client.get("/activities?action=status_change", headers=headers)
    assert res.status_code == 200
    assert len(res.json()["items"]) >= 1
    assert all(item["action"] == "status_change" for item in res.json()["items"])


def test_activities_filter_by_entity_type(client, db_session, make_token):
    emp = _create_user(db_session, "act_f_entity@example.com", "EMP_AFE")
    headers = _auth_headers(emp, make_token)

    d_id = _create_decision(client, headers).json()["id"]
    client.post(
        f"/decisions/{d_id}/alternatives",
        json={"name": "Alt", "description": "d", "pros": "p", "cons": "c"},
        headers=headers,
    )
    client.post(f"/decisions/{d_id}/comments", json={"content": "c"}, headers=headers)

    res = client.get("/activities?entity_type=alternative", headers=headers)
    assert res.status_code == 200
    assert all(item["entity_type"] == "alternative" for item in res.json()["items"])

    res = client.get("/activities?entity_type=comment", headers=headers)
    assert res.status_code == 200
    assert all(item["entity_type"] == "comment" for item in res.json()["items"])


def test_activities_filter_by_user(client, db_session, make_token):
    admin = _create_user(db_session, "act_f_user_admin@example.com", "EMP_AFUA", UserRole.ADMINISTRATOR)
    emp = _create_user(db_session, "act_f_user_emp@example.com", "EMP_AFUE")
    headers_admin = _auth_headers(admin, make_token)
    headers_emp = _auth_headers(emp, make_token)

    _create_decision(client, headers_admin)
    _create_decision(client, headers_emp)

    res = client.get(f"/activities?user={emp.id}", headers=headers_admin)
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 1
    assert body["items"][0]["user_id"] == emp.id


def test_activities_pagination(client, db_session, make_token):
    emp = _create_user(db_session, "act_page@example.com", "EMP_AP")
    headers = _auth_headers(emp, make_token)

    # Create 3 decisions
    for _ in range(3):
        _create_decision(client, headers)

    # Page 1: limit=2
    res = client.get("/activities?limit=2&offset=0", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert len(body["items"]) == 2
    assert body["total"] == 3
    assert body["has_more"] is True
    assert body["offset"] == 0
    assert body["limit"] == 2

    # Page 2: limit=2, offset=2
    res = client.get("/activities?limit=2&offset=2", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert len(body["items"]) == 1
    assert body["total"] == 3
    assert body["has_more"] is False

    # Page 3: limit=2, offset=4 (past end)
    res = client.get("/activities?limit=2&offset=4", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert len(body["items"]) == 0
    assert body["has_more"] is False


def test_activities_date_filter(client, db_session, make_token):
    emp = _create_user(db_session, "act_date@example.com", "EMP_AD")
    headers = _auth_headers(emp, make_token)

    _create_decision(client, headers)

    from datetime import date
    today = date.today().isoformat()

    res = client.get(f"/activities?start_date={today}", headers=headers)
    assert res.status_code == 200
    assert res.json()["total"] >= 1

    res = client.get("/activities?start_date=2099-01-01", headers=headers)
    assert res.status_code == 200
    assert res.json()["total"] == 0


def test_activities_invalid_date_422(client, db_session, make_token):
    emp = _create_user(db_session, "act_inv_date@example.com", "EMP_AID")
    headers = _auth_headers(emp, make_token)

    res = client.get("/activities?start_date=not-a-date", headers=headers)
    assert res.status_code == 422
    assert "Invalid date format" in res.json()["detail"]

    res = client.get("/activities?end_date=2026-13-45", headers=headers)
    assert res.status_code == 422


def test_activities_reversed_date_range_422(client, db_session, make_token):
    emp = _create_user(db_session, "act_rev_date@example.com", "EMP_ARD")
    headers = _auth_headers(emp, make_token)

    res = client.get("/activities?start_date=2026-12-31&end_date=2026-01-01", headers=headers)
    assert res.status_code == 422
    assert "start_date must not be after end_date" in res.json()["detail"]


def test_activities_require_token(client):
    res = client.get("/activities")
    assert res.status_code == 401
    assert res.json()["detail"] == "Not authenticated"


# ── Part D: Analytics Date Filters ───────────────────────────────────────────

def test_admin_analytics_date_filter(client, db_session, make_token):
    admin = _create_user(db_session, "dash_an_date@example.com", "EMP_DAND", UserRole.ADMINISTRATOR)
    headers = _auth_headers(admin, make_token)

    _create_decision(client, headers)

    from datetime import date
    today = date.today().isoformat()

    res = client.get(f"/dashboard/admin/analytics?start_date={today}", headers=headers)
    assert res.status_code == 200
    assert res.json()["decision_stats"]["total"] >= 1

    res = client.get("/dashboard/admin/analytics?start_date=2099-01-01", headers=headers)
    assert res.status_code == 200
    assert res.json()["decision_stats"]["total"] == 0


def test_admin_analytics_invalid_date_422(client, db_session, make_token):
    admin = _create_user(db_session, "dash_an_inv@example.com", "EMP_DANI", UserRole.ADMINISTRATOR)
    headers = _auth_headers(admin, make_token)

    res = client.get("/dashboard/admin/analytics?start_date=bad-date", headers=headers)
    assert res.status_code == 422
    assert "Invalid date format" in res.json()["detail"]


def test_admin_analytics_reversed_date_422(client, db_session, make_token):
    admin = _create_user(db_session, "dash_an_rev@example.com", "EMP_DANR", UserRole.ADMINISTRATOR)
    headers = _auth_headers(admin, make_token)

    res = client.get("/dashboard/admin/analytics?start_date=2026-12-31&end_date=2026-01-01", headers=headers)
    assert res.status_code == 422


def test_admin_decision_activity_date_filter(client, db_session, make_token):
    admin = _create_user(db_session, "dash_da_date@example.com", "EMP_DADD", UserRole.ADMINISTRATOR)
    headers = _auth_headers(admin, make_token)

    _create_decision(client, headers)

    from datetime import date
    today = date.today().isoformat()

    res = client.get(f"/dashboard/admin/decision-activity?start_date={today}", headers=headers)
    assert res.status_code == 200
    assert sum(d["count"] for d in res.json()["data"]) >= 1

    res = client.get("/dashboard/admin/decision-activity?start_date=2099-01-01", headers=headers)
    assert res.status_code == 200
    assert sum(d["count"] for d in res.json()["data"]) == 0


def test_admin_decision_activity_invalid_date_422(client, db_session, make_token):
    admin = _create_user(db_session, "dash_da_inv@example.com", "EMP_DADI", UserRole.ADMINISTRATOR)
    headers = _auth_headers(admin, make_token)

    res = client.get("/dashboard/admin/decision-activity?end_date=xyz", headers=headers)
    assert res.status_code == 422


def test_admin_dashboard_endpoints_require_token(client):
    for url in [
        "/dashboard/admin/approval-statistics",
        "/dashboard/admin/user-activity",
        "/dashboard/admin/analytics",
        "/dashboard/admin/decision-activity",
    ]:
        res = client.get(url)
        assert res.status_code == 401
        assert res.json()["detail"] == "Not authenticated"
