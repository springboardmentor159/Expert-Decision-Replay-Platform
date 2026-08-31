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
