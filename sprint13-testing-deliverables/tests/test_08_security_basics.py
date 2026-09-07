"""
Sprint 13 - Section 28: Security Testing (application-level, black box)

Deeper security testing (SAST, dependency scanning, pen-testing) is out
of scope for a black-box pytest suite; this file covers what's directly
observable through the API.
"""


def test_password_is_never_returned_in_user_response(api, employee_user):
    resp = api.get(f"/users/{employee_user['id']}", headers=employee_user["headers"])
    assert resp.status_code == 200
    body = resp.json()
    assert "password" not in body
    assert "hashed_password" not in body


def test_password_not_echoed_on_creation_response(api, new_employee):
    # new_employee fixture already performed the create+login round trip;
    # re-fetch to make sure the stored representation never leaks it.
    resp = api.get(f"/users/{new_employee['id']}", headers=new_employee["headers"])
    assert resp.status_code == 200
    assert "password" not in resp.json()


def test_login_failure_message_does_not_reveal_which_field_was_wrong(api, employee_user):
    """Login errors should say 'invalid email or password', not confirm
    whether the email exists - this avoids user enumeration."""
    bad_user_resp = api.post(
        "/users/login",
        data={"username": "no-such-account@sprint13.test", "password": "whatever"},
    )
    bad_password_resp = api.post(
        "/users/login",
        data={"username": employee_user["email"], "password": "wrong-password"},
    )
    assert bad_user_resp.status_code == bad_password_resp.status_code == 401
    assert bad_user_resp.json()["detail"] == bad_password_resp.json()["detail"]


def test_sql_injection_style_search_keyword_is_handled_safely(api, employee_user):
    """The ORM should parameterize this; it must come back as a normal
    (possibly empty) result set, never a 500."""
    resp = api.get(
        "/decisions/search",
        params={"q": "' OR '1'='1"},
        headers=employee_user["headers"],
    )
    assert resp.status_code == 200
    assert "items" in resp.json()


def test_cannot_access_other_users_pending_approval_action(
    api, employee_user, reviewer_user, manager_user, draft_decision
):
    """Only the assigned reviewer (or an Administrator) may act on an
    approval - already enforced by the code (see approval.py), tested
    here as a regression guard."""
    api.patch(
        f"/decisions/{draft_decision['id']}/status",
        json={"status": "Under Review"},
        headers=employee_user["headers"],
    )
    assign = api.post(
        f"/decisions/{draft_decision['id']}/approvals",
        json={"level": 1, "reviewer_id": reviewer_user["id"]},
        headers=manager_user["headers"],
    )
    assert assign.status_code == 201
    approval_id = assign.json()["id"]

    resp = api.patch(
        f"/approvals/{approval_id}",
        json={"decision": "Approved"},
        headers=employee_user["headers"],
    )
    assert resp.status_code == 403
