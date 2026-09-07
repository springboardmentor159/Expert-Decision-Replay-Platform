# Sprint 13 - Bug Tracker

Format follows spec Section 32/33: Bug ID, Module, Description, Steps to
Reproduce, Expected Result, Actual Result, Severity, Status.

These were found by reading `expert-decision-replay/app` against the
Sprint 13 requirements doc and are also encoded as `xfail`-marked tests
in `tests/` so they show up automatically the next time the suite runs
(and stop being `xfail` the moment they're fixed).

---

## BUG-001 — User management has no role guard
**Module:** Users (`app/routers/users.py`)
**Severity:** High
**Status:** Open
**Reproduce:**
1. Register/login as an `Employee`.
2. `GET /users/` with the Employee's token.
3. `PUT /users/{other_user_id}` with `{"role": "Administrator"}`.
4. `DELETE /users/{other_user_id}`.

**Expected result:** Spec Section 6/7 reserves user management for the
`Administrator` role — list/update/delete on arbitrary users should
return `403 Forbidden` for non-admins.
**Actual result:** All four operations succeed for *any* authenticated
user, regardless of role — an Employee can list every user, promote
themself or anyone else to Administrator, or delete another account.
**Suggested fix:** wrap `get_users`, `get_user` (for a *different* id
than `current_user.id`), `update_user`, and `delete_user` with
`Depends(require_role("Administrator"))`, the same pattern already used
correctly in `dashboard.py`, `audit.py`, and `report.py`. A drop-in
patched version is included at `fixes/users_router_patch.py`.

---

## BUG-002 — Decision status endpoint accepts any transition
**Module:** Decisions (`app/routers/decision.py`, `PATCH /decisions/{id}/status`)
**Severity:** High
**Status:** Open
**Reproduce:**
1. Create a decision (`Draft`).
2. `PATCH /decisions/{id}/status {"status": "Approved"}` — succeeds,
   skipping `Under Review` entirely.
3. Archive the decision, then `PATCH .../status {"status": "Draft"}` —
   also succeeds.

**Expected result:** Spec Section 8 requires the backend to enforce a
state-transition table and explicitly calls out `Archived → Draft` as
an example of a transition that must be rejected unless the business
rules explicitly allow it.
**Actual result:** The endpoint accepts any member of `DecisionStatus`
as the next value with no adjacency check.
**Suggested fix:** add a `VALID_TRANSITIONS` map (e.g. `Draft →
{Under Review, Archived}`, `Under Review → {Approved, Rejected}`,
`Approved → {Archived}`, `Rejected → {Archived}`, `Archived → {}`) and
return `422` for anything not in the set. See
`fixes/decision_status_transition_patch.py` for a ready-to-drop-in
version of the endpoint.

---

## BUG-003 — Multi-level approval does not actually cascade
**Module:** Approvals (`app/routers/approval.py`, `PATCH /approvals/{id}`)
**Severity:** Medium
**Status:** Open
**Reproduce:**
1. Submit a decision for review.
2. Assign a Level-1 reviewer *and* a Level-2 manager approval
   (`POST /decisions/{id}/approvals` twice, `level=1` then `level=2`).
3. Have the Level-1 reviewer approve.

**Expected result:** Per Section 4 Step 10, a second-level approval
should still be required before the decision is finally `Approved`;
the decision should move to some "level 1 cleared, awaiting level 2"
state, not directly to `Approved`.
**Actual result:** `act_on_approval` sets `decision.status` directly to
`Approved`/`Rejected` on *any* single approval action, regardless of
`level`. The Level-2 approval record is left permanently `Pending`
against a decision that's already in a terminal status.
**Suggested fix:** only flip `decision.status` when the *highest*
pending `level` for that decision has been actioned, or introduce an
explicit `all levels approved` check before finalizing.

---

## BUG-004 — `AuditLog.old_value`/`new_value` use a Postgres-only column type
**Module:** Audit (`app/models/audit_log.py`)
**Severity:** Low (informational / testing note)
**Status:** Open
**Detail:** `old_value`/`new_value` are declared as
`sqlalchemy.dialects.postgresql.JSONB`. This is correct and intentional
for production (the project already standardizes on Postgres via
`psycopg2-binary` in `requirements.txt`), but it means the test suite
in this deliverable, or any future one, **cannot** run against SQLite —
it must run against a real Postgres instance. `tests/conftest.py`
documents this; flagging it here too so it isn't rediscovered the hard
way while wiring up CI.
**Suggested action:** none required functionally; when adding a CI
pipeline, provision a throwaway Postgres service container rather than
defaulting to SQLite for speed.

---

## Regression coverage
All four items above have a corresponding automated test in `tests/`
(marked `@pytest.mark.xfail(strict=False, reason="BUG-00x...")` for the
three functional bugs). Once a fix ships, remove the `xfail` marker —
if the test then passes, the suite proves the regression is closed; if
it still fails, CI will flag it immediately as a real failure instead of
a silently-skipped known issue.
