# Sprint 13 — System Integration, Testing & Bug Fixing
### Deliverable package for `Expert Decision Replay Platform`

This package implements the testing work described in the Sprint 13
brief, targeted at the actual codebase found in
`infosys-project/expert-decision-replay` inside your uploaded zip
(the `Expert-Decision-Replay-Platform` folder in the same zip is an
older/duplicate scaffold and was not used).

It is **black-box API testing** (pytest + `requests`, plus a Postman
collection) run against your live FastAPI app and a real Postgres
database — not mocks. This is required here because
`AuditLog.old_value` / `new_value` use SQLAlchemy's
`postgresql.JSONB` column type (see `BUG_TRACKER.md`, BUG-004), which
only exists on Postgres.

## Contents

```
tests/                          pytest suite (8 modules, ~60 test cases)
  conftest.py                   fixtures: live-API session, per-role users, decision factory
  test_01_auth.py               Section 5 — Authentication
  test_02_authorization.py      Section 6/7 — Authorization & role matrix
  test_03_decision_validation.py Section 9 — Validation (422s)
  test_04_error_handling.py     Section 10 — 404/401/403/422, no leaked tracebacks
  test_05_decision_state_transitions.py  Section 8 — status transitions
  test_06_full_decision_lifecycle_e2e.py Sections 4/21/34 — the full workflow
  test_07_dashboard_and_reports.py       Sections 15-19 — dashboards, search, reports, exports
  test_08_security_basics.py    Section 28 — password exposure, enumeration, SQLi-safety
postman/                        Section 25 — Postman collection + environment
BUG_TRACKER.md                  Section 32/33 — bugs found, severity, suggested fixes
fixes/                          Ready-to-apply patches for the High-severity bugs
.env.example                    Section 29 — placeholder config (no real secrets)
requirements-test.txt           Test-only dependencies
pytest.ini
```

## Running the tests

1. Start the API against a real (throwaway/test) Postgres database:
   ```bash
   cd expert-decision-replay
   cp .env.example .env        # fill in DATABASE_URL / SECRET_KEY
   uvicorn app.main:app --reload
   ```
2. In a separate shell, from this package's root:
   ```bash
   pip install -r requirements-test.txt --break-system-packages
   export API_BASE_URL=http://localhost:8000     # default, can be omitted
   pytest -v
   ```
   For an HTML report: `pytest --html=report.html --self-contained-html`.

Each test run registers fresh, uniquely-suffixed users
(`employee.<run-id>-<n>@sprint13.test`, etc.) so it's safe to re-run the
suite repeatedly without manual DB cleanup — email/employee_id
uniqueness constraints are respected automatically.

### Expected results on the *current* code

Three tests are intentionally marked `xfail` because they encode rules
the spec requires but the current implementation doesn't yet enforce
(see `BUG_TRACKER.md` BUG-001/002). They will show as `x` (expected
failure) in pytest output, not as red failures — that's correct. Once
you apply the corresponding fix in `fixes/`, remove the `xfail` marker
from that test so it becomes a normal regression check.

## Postman

Import both files in `postman/` into Postman. Run **Authentication →
Users → Decisions → Alternatives → Discussion → Approvals → Dashboard
→ Audit → Reports**, in that order (top to bottom in the sidebar, or
via Collection Runner) — later requests depend on variables
(`decision_id`, `approval_id`, etc.) that earlier requests populate
via test scripts. `{{reviewer_jwt_token}}`, `{{manager_jwt_token}}`,
and `{{admin_jwt_token}}` need to be set once by logging in as those
roles the same way the "Login" request does for the Employee — add a
"Login as Reviewer/Manager/Admin" request per your actual seeded users,
or duplicate the Employee login request and swap the credentials.

## What's *not* included

Per Section 30/31 (code cleanup, Swagger doc review) and Section 26/27
(performance and concurrency testing under load), those are manual /
tooling-assisted activities against your running instance and codebase
rather than something a generated file can do for you:

- **Swagger**: open `/docs` on your running instance and click through
  each endpoint listed in Section 24 — the Postman collection above
  exercises the same surface if you'd rather automate it.
- **Performance/concurrency (Sections 26-27)**: use a load tool such as
  `locust` or `k6` against the endpoints called out in Section 26
  (login, decision search, dashboard stats, report generation) once the
  functional bugs above are fixed, since BUG-003 in particular would
  otherwise produce misleading concurrency results on the approvals
  endpoint.
- **Code cleanup / dead code removal (Section 30)**: requires editing
  your working tree directly; `fixes/` gives you a starting point for
  the two highest-severity items but a full pass is still a manual
  review of the existing files.

## Bugs found during this pass

See `BUG_TRACKER.md` for the full write-up. Summary:

| ID | Module | Severity | Status |
|----|--------|----------|--------|
| BUG-001 | Users — no role guard on list/update/delete | High | Open (fix in `fixes/users_router_patch.py`) |
| BUG-002 | Decisions — status endpoint accepts any transition | High | Open (fix in `fixes/decision_status_transition_patch.py`) |
| BUG-003 | Approvals — multi-level approval doesn't cascade | Medium | Open |
| BUG-004 | Audit — JSONB column is Postgres-only | Low / informational | N/A (by design; documented for CI setup) |

Per Section 33, BUG-001 and BUG-002 (High severity) should be resolved
before the sprint is considered complete.
