"""
Sprint 13 - Section 9: Validation Testing

Every case here expects HTTP 422 (FastAPI/Pydantic's validation-error
status), per the spec.
"""
import pytest


def test_create_decision_missing_required_field_is_422(api, employee_user):
    resp = api.post(
        "/decisions",
        json={"problem_statement": "Missing the title field"},
        headers=employee_user["headers"],
    )
    assert resp.status_code == 422


def test_create_user_missing_required_field_is_422(api):
    resp = api.post(
        "/users/",
        json={
            "full_name": "No Email Person",
            # "email" intentionally omitted
            "role": "Employee",
            "password": "P@ssw0rd!",
            "employee_id": "EMP-VALID-001",
            "department": "QA",
            "designation": "Employee",
            "phone_number": "9000000001",
        },
    )
    assert resp.status_code == 422


def test_create_user_invalid_email_is_422(api):
    resp = api.post(
        "/users/",
        json={
            "full_name": "Bad Email Person",
            "email": "not-an-email",
            "role": "Employee",
            "password": "P@ssw0rd!",
            "employee_id": "EMP-VALID-002",
            "department": "QA",
            "designation": "Employee",
            "phone_number": "9000000002",
        },
    )
    assert resp.status_code == 422


def test_create_user_invalid_role_is_422(api):
    resp = api.post(
        "/users/",
        json={
            "full_name": "Bad Role Person",
            "email": "bad.role@sprint13.test",
            "role": "Superuser",
            "password": "P@ssw0rd!",
            "employee_id": "EMP-VALID-003",
            "department": "QA",
            "designation": "Employee",
            "phone_number": "9000000003",
        },
    )
    assert resp.status_code == 422


@pytest.mark.parametrize("bad_score", [0, 6, -1, 100])
def test_alternative_feasibility_score_out_of_range_is_422(
    api, employee_user, draft_decision, bad_score
):
    resp = api.post(
        f"/decisions/{draft_decision['id']}/alternatives",
        json={
            "name": "PostgreSQL",
            "description": "Relational database",
            "pros": "Mature, ACID-compliant",
            "cons": "Vertical scaling limits",
            "estimated_cost": 5000,
            "feasibility_score": bad_score,
            "risk_level": "Low",
        },
        headers=employee_user["headers"],
    )
    assert resp.status_code == 422, f"score={bad_score} should be rejected"


def test_alternative_invalid_risk_level_is_422(api, employee_user, draft_decision):
    resp = api.post(
        f"/decisions/{draft_decision['id']}/alternatives",
        json={
            "name": "MongoDB",
            "description": "Document database",
            "pros": "Flexible schema",
            "cons": "Weaker consistency guarantees",
            "estimated_cost": 4000,
            "feasibility_score": 4,
            "risk_level": "Very Dangerous",
        },
        headers=employee_user["headers"],
    )
    assert resp.status_code == 422


def test_alternative_missing_required_field_is_422(api, employee_user, draft_decision):
    resp = api.post(
        f"/decisions/{draft_decision['id']}/alternatives",
        json={
            "name": "MySQL",
            # description, pros, cons, estimated_cost intentionally omitted
            "feasibility_score": 4,
            "risk_level": "Low",
        },
        headers=employee_user["headers"],
    )
    assert resp.status_code == 422


def test_decision_invalid_status_value_is_422(api, employee_user, draft_decision):
    resp = api.patch(
        f"/decisions/{draft_decision['id']}/status",
        json={"status": "Cancelled"},  # not a member of DecisionStatus
        headers=employee_user["headers"],
    )
    assert resp.status_code == 422


def test_decision_id_non_integer_is_422(api, employee_user):
    resp = api.get("/decisions/abc", headers=employee_user["headers"])
    assert resp.status_code == 422


def test_alternative_id_non_integer_is_422(api, employee_user):
    resp = api.get("/alternatives/xyz", headers=employee_user["headers"])
    assert resp.status_code == 422


def test_approval_action_invalid_decision_value_is_422(
    api, employee_user, manager_user, reviewer_user, draft_decision
):
    assign = api.post(
        f"/decisions/{draft_decision['id']}/approvals",
        json={"level": 1, "reviewer_id": reviewer_user["id"]},
        headers=manager_user["headers"],
    )
    assert assign.status_code == 201
    approval_id = assign.json()["id"]

    resp = api.patch(
        f"/approvals/{approval_id}",
        json={"decision": "Maybe"},  # only Approve/Reject should be valid
        headers=reviewer_user["headers"],
    )
    assert resp.status_code == 422
