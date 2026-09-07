"""
Sprint 13 - Section 8: Decision State Testing

Valid statuses: Draft, Under Review, Approved, Rejected, Archived.
The spec requires the backend to enforce state-transition rules (e.g.
Archived -> Draft must never be allowed).

NOTE: as shipped, PATCH /decisions/{id}/status does not yet validate
that the requested transition is legal - see BUG-002 in BUG_TRACKER.md.
The xfail-marked tests below encode the *intended* rule; remove the
marker once the fix lands and they become ordinary regression tests.
"""
import pytest


def _set_status(api, headers, decision_id, new_status):
    return api.patch(
        f"/decisions/{decision_id}/status",
        json={"status": new_status},
        headers=headers,
    )


def test_draft_to_under_review_is_allowed(api, employee_user, draft_decision):
    resp = _set_status(api, employee_user["headers"], draft_decision["id"], "Under Review")
    assert resp.status_code == 200
    assert resp.json()["status"] == "Under Review"


def test_under_review_to_approved_is_allowed(api, employee_user, draft_decision):
    _set_status(api, employee_user["headers"], draft_decision["id"], "Under Review")
    resp = _set_status(api, employee_user["headers"], draft_decision["id"], "Approved")
    assert resp.status_code == 200
    assert resp.json()["status"] == "Approved"


def test_approved_to_archived_is_allowed(api, employee_user, draft_decision):
    _set_status(api, employee_user["headers"], draft_decision["id"], "Under Review")
    _set_status(api, employee_user["headers"], draft_decision["id"], "Approved")
    resp = _set_status(api, employee_user["headers"], draft_decision["id"], "Archived")
    assert resp.status_code == 200
    assert resp.json()["status"] == "Archived"


@pytest.mark.xfail(
    reason="BUG-002: the status endpoint accepts ANY DecisionStatus value "
    "as the next status with no transition-table check, so Archived -> "
    "Draft currently succeeds instead of being rejected.",
    strict=False,
)
def test_archived_to_draft_is_rejected(api, employee_user, draft_decision):
    _set_status(api, employee_user["headers"], draft_decision["id"], "Under Review")
    _set_status(api, employee_user["headers"], draft_decision["id"], "Approved")
    _set_status(api, employee_user["headers"], draft_decision["id"], "Archived")

    resp = _set_status(api, employee_user["headers"], draft_decision["id"], "Draft")
    assert resp.status_code in (400, 409, 422)


@pytest.mark.xfail(
    reason="BUG-002: see above - Draft -> Approved should not be allowed "
    "to skip the review step entirely.",
    strict=False,
)
def test_draft_to_approved_directly_is_rejected(api, employee_user, draft_decision):
    resp = _set_status(api, employee_user["headers"], draft_decision["id"], "Approved")
    assert resp.status_code in (400, 409, 422)


def test_update_on_archived_decision_is_forbidden(api, employee_user, draft_decision):
    """This part of the state rules *is* enforced today."""
    _set_status(api, employee_user["headers"], draft_decision["id"], "Under Review")
    _set_status(api, employee_user["headers"], draft_decision["id"], "Approved")
    _set_status(api, employee_user["headers"], draft_decision["id"], "Archived")

    resp = api.put(
        f"/decisions/{draft_decision['id']}",
        json={"title": "Trying to edit an archived decision"},
        headers=employee_user["headers"],
    )
    assert resp.status_code == 403
