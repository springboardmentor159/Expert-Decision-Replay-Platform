# Sprint 13 Test Report

## Automated baseline

Command:

```text
venv\Scripts\python.exe -m pytest -q
```

Result: `7 passed`.

The configured suite uses `tests/` through `pytest.ini`. Manual Sprint 6 scripts remain available for live-server/Postman-style checks but are not collected as pytest tests because they call `http://localhost:8000` directly.

## Bugs found and fixed

| ID | Module | Description | Severity | Status | Fix |
| --- | --- | --- | --- | --- | --- |
| BUG-013-001 | Decision authorization | Any authenticated user could update, change status, archive, or change rationale on another user's decision. | High | Fixed | Enforced owner-or-manager/admin authorization on decision mutations. |
| BUG-013-002 | Decision lifecycle | Status updates allowed invalid jumps such as `Draft` to `Approved` and changes after archival. | High | Fixed | Added explicit status transition rules and `409 Conflict` responses. |
| BUG-013-003 | Test infrastructure | Default pytest discovery executed manual live-server scripts and failed when port 8000 was not running. | Medium | Fixed | Restricted pytest discovery to maintained in-process tests. |
| BUG-013-004 | Security/configuration | Default settings contained a database password and non-production JWT secret. | High | Fixed | Added `.env.example` placeholders and replaced defaults with development-safe values. |

## Coverage completed

- Authentication and protected endpoint regression tests
- Decision creation and retrieval
- Decision ownership authorization
- Valid and invalid decision status transitions
- Archived decision immutability
- Password hashing and login flow
- Existing decision regression tests

## Remaining manual/infrastructure checks

The following Sprint 13 areas require a running PostgreSQL/test environment and/or external verification: multi-role approval sequences, file upload behavior, dashboard/report exports, concurrent requests, performance, pgAdmin relationship checks, Swagger/Postman walkthrough, and final GitHub push verification.
