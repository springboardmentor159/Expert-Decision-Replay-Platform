"""
Sprint 13 - Section 10: Error Handling Testing
"""


def test_get_nonexistent_user_is_404(api, employee_user):
    resp = api.get("/users/999999999", headers=employee_user["headers"])
    assert resp.status_code == 404


def test_get_nonexistent_decision_is_404(api, employee_user):
    resp = api.get("/decisions/999999999", headers=employee_user["headers"])
    assert resp.status_code == 404


def test_get_nonexistent_alternative_is_404(api, employee_user):
    resp = api.get("/alternatives/999999999", headers=employee_user["headers"])
    assert resp.status_code == 404


def test_get_nonexistent_approval_action_is_404(api, employee_user):
    resp = api.patch(
        "/approvals/999999999",
        json={"decision": "Approved"},
        headers=employee_user["headers"],
    )
    assert resp.status_code == 404


def test_create_alternative_for_nonexistent_decision_is_404(api, employee_user):
    resp = api.post(
        "/decisions/999999999/alternatives",
        json={
            "name": "PostgreSQL",
            "description": "x",
            "pros": "x",
            "cons": "x",
            "estimated_cost": 1,
            "feasibility_score": 3,
            "risk_level": "Low",
        },
        headers=employee_user["headers"],
    )
    assert resp.status_code == 404


def test_create_comment_for_nonexistent_decision_is_404(api, employee_user):
    resp = api.post(
        "/decisions/999999999/comments",
        json={"content": "hello"},
        headers=employee_user["headers"],
    )
    assert resp.status_code == 404


def test_malformed_json_body_is_422(api, employee_user):
    resp = api.post(
        "/decisions",
        data="{not valid json",
        headers={
            **employee_user["headers"],
            "Content-Type": "application/json",
        },
    )
    assert resp.status_code == 422


def test_missing_jwt_on_write_operation_is_401(api):
    resp = api.post(
        "/decisions",
        json={
            "title": "Should never be created",
            "problem_statement": "no auth supplied",
            "category": "Technology",
        },
    )
    assert resp.status_code == 401


def test_insufficient_permission_on_admin_report_is_403(api, employee_user):
    resp = api.get("/reports/audit", headers=employee_user["headers"])
    assert resp.status_code == 403


def test_insufficient_permission_on_admin_audit_logs_is_403(api, employee_user):
    resp = api.get("/audit-logs", headers=employee_user["headers"])
    assert resp.status_code == 403


def test_error_response_never_leaks_traceback(api, employee_user):
    """A 404/422/etc body should be a clean JSON error, never a raw
    stack trace or 500 for a plain not-found lookup."""
    resp = api.get("/decisions/999999999", headers=employee_user["headers"])
    assert resp.status_code == 404
    body = resp.json()
    assert "detail" in body
    assert "Traceback" not in resp.text
