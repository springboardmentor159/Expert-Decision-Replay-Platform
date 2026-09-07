"""
Sprint 13 - Shared pytest fixtures.

These tests run as BLACK-BOX API tests against a *live, running* instance
of the Expert Decision Replay Platform (the same way Swagger/Postman would
exercise it), backed by a real PostgreSQL database - not a mocked DB.
This matters because AuditLog.old_value/new_value use SQLAlchemy's
postgresql.JSONB column type, which only works against real Postgres.

Usage:
    1. Start the API (uvicorn app.main:app --reload) against a Postgres
       database you don't mind filling with test data.
    2. export API_BASE_URL=http://localhost:8000   (defaults to this)
    3. pip install -r requirements-test.txt
    4. pytest -v
"""
import os
import uuid
import random

import pytest
import requests

BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000").rstrip("/")

# A short id unique to this test run so re-running the suite never
# collides with previously-created users (email / employee_id are unique).
RUN_ID = uuid.uuid4().hex[:8]


# ---------------------------------------------------------------------
# Low-level HTTP helpers
# ---------------------------------------------------------------------

@pytest.fixture(scope="session")
def api():
    session = requests.Session()

    class Api:
        base_url = BASE_URL

        def url(self, path: str) -> str:
            return f"{BASE_URL}{path}"

        def post(self, path, **kw):
            return session.post(self.url(path), **kw)

        def get(self, path, **kw):
            return session.get(self.url(path), **kw)

        def put(self, path, **kw):
            return session.put(self.url(path), **kw)

        def patch(self, path, **kw):
            return session.patch(self.url(path), **kw)

        def delete(self, path, **kw):
            return session.delete(self.url(path), **kw)

    return Api()


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------
# User factory
# ---------------------------------------------------------------------

def _register_and_login(api, role: str, tag: str):
    """Registers a brand-new user with the given role and logs them in.
    Returns dict with id, email, password, token, role.
    """
    suffix = f"{RUN_ID}-{tag}-{random.randint(1000, 9999)}"
    email = f"{tag}.{suffix}@example.com"
    password = "P@ssw0rd!2026"

    payload = {
        "full_name": f"{tag.title()} Tester {suffix}",
        "email": email,
        "role": role,
        "password": password,
        "employee_id": f"EMP-{suffix}",
        "department": "Quality Engineering",
        "designation": role,
        "phone_number": "9000000000",
    }

    resp = api.post("/users/", json=payload)
    assert resp.status_code == 201, (
        f"Failed to register {role} test user: "
        f"{resp.status_code} {resp.text}"
    )
    user = resp.json()

    login_resp = api.post(
        "/users/login",
        data={"username": email, "password": password},
    )
    assert login_resp.status_code == 200, (
        f"Failed to log in freshly-registered {role} user: "
        f"{login_resp.status_code} {login_resp.text}"
    )
    token = login_resp.json()["access_token"]

    return {
        "id": user["id"],
        "email": email,
        "password": password,
        "role": role,
        "token": token,
        "headers": auth_headers(token),
    }


@pytest.fixture(scope="session")
def employee_user(api):
    return _register_and_login(api, "Employee", "employee")


@pytest.fixture(scope="session")
def reviewer_user(api):
    return _register_and_login(api, "Reviewer", "reviewer")


@pytest.fixture(scope="session")
def manager_user(api):
    return _register_and_login(api, "Manager", "manager")


@pytest.fixture(scope="session")
def admin_user(api):
    return _register_and_login(api, "Administrator", "admin")


@pytest.fixture()
def new_employee(api):
    """A fresh Employee user, function-scoped, for tests that must not
    share state (e.g. registration/duplicate-email checks)."""
    return _register_and_login(api, "Employee", "emp-fn")


# ---------------------------------------------------------------------
# Decision factory (used by several test modules)
# ---------------------------------------------------------------------

@pytest.fixture()
def draft_decision(api, employee_user):
    """Creates a fresh Draft decision owned by the session Employee user."""
    resp = api.post(
        "/decisions",
        json={
            "title": f"Database selection {uuid.uuid4().hex[:6]}",
            "problem_statement": "We need to choose a primary datastore.",
            "category": "Technology",
        },
        headers=employee_user["headers"],
    )
    assert resp.status_code == 201, resp.text
    return resp.json()
