"""
Sprint 13 - Section 5: Authentication Testing

Covers: valid login, invalid username, invalid password, missing
username/password, missing/invalid/expired JWT, and accessing a
protected endpoint without authentication.
"""
import time

import jwt as pyjwt
import pytest


def test_valid_login_returns_bearer_token(api, employee_user):
    resp = api.post(
        "/users/login",
        data={
            "username": employee_user["email"],
            "password": employee_user["password"],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_invalid_username_rejected(api):
    resp = api.post(
        "/users/login",
        data={"username": "nobody-at-all@example.com", "password": "whatever"},
    )
    assert resp.status_code == 401


def test_login_invalid_password_rejected(api, employee_user):
    resp = api.post(
        "/users/login",
        data={"username": employee_user["email"], "password": "wrong-password"},
    )
    assert resp.status_code == 401


def test_login_missing_username_is_rejected(api, employee_user):
    resp = api.post(
        "/users/login",
        data={"password": employee_user["password"]},
    )
    # OAuth2PasswordRequestForm makes both fields required -> 422
    assert resp.status_code == 422


def test_login_missing_password_is_rejected(api, employee_user):
    resp = api.post(
        "/users/login",
        data={"username": employee_user["email"]},
    )
    assert resp.status_code == 422


def test_protected_endpoint_without_token_is_401(api):
    resp = api.get("/decisions")
    assert resp.status_code == 401


def test_protected_endpoint_with_malformed_token_is_401(api):
    resp = api.get(
        "/decisions",
        headers={"Authorization": "Bearer not-a-real-jwt"},
    )
    assert resp.status_code == 401


def test_protected_endpoint_with_garbage_bearer_scheme_is_401(api):
    resp = api.get("/decisions", headers={"Authorization": "Token abc123"})
    assert resp.status_code == 401


def test_protected_endpoint_with_forged_token_wrong_secret_is_401(api, employee_user):
    """A token signed with the wrong secret must never be trusted, even if
    the payload (sub) matches a real user id."""
    forged = pyjwt.encode(
        {"sub": str(employee_user["id"]), "exp": int(time.time()) + 3600},
        "definitely-not-the-real-secret",
        algorithm="HS256",
    )
    resp = api.get("/decisions", headers={"Authorization": f"Bearer {forged}"})
    assert resp.status_code == 401


def test_protected_endpoint_with_expired_token_is_401(api, employee_user):
    """Builds a token that is already expired to confirm expiry is
    enforced. NOTE: this only works if the test can reuse the app's
    actual SECRET_KEY (see SECRET_KEY_FOR_TESTS below); if it is not
    supplied, this test is skipped rather than giving a false pass/fail.
    """
    import os

    secret = os.environ.get("SECRET_KEY_FOR_TESTS")
    if not secret:
        pytest.skip(
            "Set SECRET_KEY_FOR_TESTS to the API's SECRET_KEY to exercise "
            "true JWT-expiry testing."
        )

    expired = pyjwt.encode(
        {"sub": str(employee_user["id"]), "exp": int(time.time()) - 60},
        secret,
        algorithm="HS256",
    )
    resp = api.get("/decisions", headers={"Authorization": f"Bearer {expired}"})
    assert resp.status_code == 401


def test_duplicate_email_registration_is_rejected(api, new_employee):
    resp = api.post(
        "/users/",
        json={
            "full_name": "Duplicate Person",
            "email": new_employee["email"],
            "role": "Employee",
            "password": "AnotherP@ss1",
            "employee_id": "EMP-DUP-999",
            "department": "QA",
            "designation": "Employee",
            "phone_number": "9111111111",
        },
    )
    assert resp.status_code == 400


def test_duplicate_employee_id_registration_is_rejected(api, new_employee):
    resp = api.post(
        "/users/",
        json={
            "full_name": "Duplicate Person 2",
            "email": "totally-different-email@example.com",
            "role": "Employee",
            "password": "AnotherP@ss1",
            "employee_id": new_employee["id"] and _employee_id_of(api, new_employee),
            "department": "QA",
            "designation": "Employee",
            "phone_number": "9222222222",
        },
    )
    print(resp.json())
    assert resp.status_code == 400


def _employee_id_of(api, user):
    resp = api.get(f"/users/{user['id']}", headers=user["headers"])
    assert resp.status_code == 200
    return resp.json()["employee_id"]
