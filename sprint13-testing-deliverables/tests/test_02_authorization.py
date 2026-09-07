"""
Sprint 13 - Section 6/7: Authorization & Role Matrix Testing

Authentication answers "who are you"; these tests answer "what are you
allowed to do". Every check re-uses one authenticated user per role
(session fixtures) so the whole role matrix is exercised without
re-registering a user per test.

Where a test is marked xfail with a BUG-xxx reference, see BUG_TRACKER.md
- the test encodes the *intended* rule from the sprint spec even though
today's implementation does not yet enforce it. Once the fix lands,
remove the xfail marker and the test becomes a normal regression check.
"""
import pytest


# ---------------------------------------------------------------------
# Admin-only surfaces
# ---------------------------------------------------------------------

ADMIN_ONLY_GET_ENDPOINTS = [
    "/dashboard/admin",
    "/dashboard/admin/analytics",
    "/dashboard/admin/user-activity",
    "/reports/audit",
    "/audit-logs",
    "/security-logs",
    "/access-logs",
]


@pytest.mark.parametrize("path", ADMIN_ONLY_GET_ENDPOINTS)
def test_admin_only_endpoint_rejects_employee(api, employee_user, path):
    resp = api.get(path, headers=employee_user["headers"])
    assert resp.status_code == 403, f"{path} should be Administrator-only"


@pytest.mark.parametrize("path", ADMIN_ONLY_GET_ENDPOINTS)
def test_admin_only_endpoint_rejects_manager(api, manager_user, path):
    resp = api.get(path, headers=manager_user["headers"])
    assert resp.status_code == 403, f"{path} should be Administrator-only"


@pytest.mark.parametrize("path", ADMIN_ONLY_GET_ENDPOINTS)
def test_admin_only_endpoint_allows_admin(api, admin_user, path):
    resp = api.get(path, headers=admin_user["headers"])
    assert resp.status_code == 200, f"{path} unexpectedly blocked an Administrator"


# ---------------------------------------------------------------------
# Manager+ surfaces
# ---------------------------------------------------------------------

MANAGER_PLUS_GET_ENDPOINTS = [
    "/dashboard/manager",
    "/dashboard/manager/team-decisions",
    "/dashboard/manager/pending-approvals",
    "/dashboard/manager/statistics",
    "/reports/teams",
]


@pytest.mark.parametrize("path", MANAGER_PLUS_GET_ENDPOINTS)
def test_manager_plus_endpoint_rejects_employee(api, employee_user, path):
    resp = api.get(path, headers=employee_user["headers"])
    assert resp.status_code == 403, f"{path} should require Manager or Administrator"


@pytest.mark.parametrize("path", MANAGER_PLUS_GET_ENDPOINTS)
def test_manager_plus_endpoint_allows_manager(api, manager_user, path):
    resp = api.get(path, headers=manager_user["headers"])
    assert resp.status_code == 200, f"{path} unexpectedly blocked a Manager"


@pytest.mark.parametrize("path", MANAGER_PLUS_GET_ENDPOINTS)
def test_manager_plus_endpoint_allows_admin(api, admin_user, path):
    resp = api.get(path, headers=admin_user["headers"])
    assert resp.status_code == 200, f"{path} unexpectedly blocked an Administrator"


# ---------------------------------------------------------------------
# Employee dashboard - every authenticated role may view their own
# ---------------------------------------------------------------------

EMPLOYEE_SELF_SERVICE_ENDPOINTS = [
    "/dashboard/employee",
    "/dashboard/employee/decisions",
    "/dashboard/employee/pending-reviews",
    "/dashboard/employee/recent-activities",
]


@pytest.mark.parametrize("path", EMPLOYEE_SELF_SERVICE_ENDPOINTS)
def test_employee_dashboard_available_to_employee(api, employee_user, path):
    resp = api.get(path, headers=employee_user["headers"])
    assert resp.status_code == 200


# ---------------------------------------------------------------------
# Approval assignment - Manager/Administrator only (already enforced)
# ---------------------------------------------------------------------

def test_employee_cannot_assign_reviewer(api, employee_user, reviewer_user, draft_decision):
    resp = api.post(
        f"/decisions/{draft_decision['id']}/approvals",
        json={"level": 1, "reviewer_id": reviewer_user["id"]},
        headers=employee_user["headers"],
    )
    assert resp.status_code == 403


def test_manager_can_assign_reviewer(api, manager_user, reviewer_user, draft_decision):
    resp = api.post(
        f"/decisions/{draft_decision['id']}/approvals",
        json={"level": 1, "reviewer_id": reviewer_user["id"]},
        headers=manager_user["headers"],
    )
    assert resp.status_code == 201


# ---------------------------------------------------------------------
# Known gaps vs. the Sprint 13 role matrix (see BUG_TRACKER.md)
# ---------------------------------------------------------------------

@pytest.mark.xfail(
    reason="BUG-001: /users list/update/delete has no role guard - any "
    "authenticated user (even Employee) can currently manage any other "
    "user. Spec section 6 reserves user management for Administrator.",
    strict=False,
)
def test_employee_cannot_list_all_users(api, employee_user):
    resp = api.get("/users/", headers=employee_user["headers"])
    assert resp.status_code == 403


@pytest.mark.xfail(
    reason="BUG-001: see above - update should be self-service or "
    "Administrator-only, not open to any authenticated user.",
    strict=False,
)
def test_employee_cannot_update_another_users_role(api, employee_user, reviewer_user):
    resp = api.put(
        f"/users/{reviewer_user['id']}",
        json={"role": "Administrator"},
        headers=employee_user["headers"],
    )
    assert resp.status_code == 403


@pytest.mark.xfail(
    reason="BUG-001: see above - delete should be Administrator-only.",
    strict=False,
)
def test_employee_cannot_delete_another_user(api, employee_user, new_employee):
    resp = api.delete(f"/users/{new_employee['id']}", headers=employee_user["headers"])
    assert resp.status_code == 403
