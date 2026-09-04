# Sprint 13 Test Report

## Integration Result

`test_sprint13_integration.py` passed against a clean Uvicorn process on port 8001 using a process-only validation secret.

Covered workflow:

- Employee, reviewer, and manager registration and login
- Missing JWT rejection
- Duplicate registration rollback with `409 Conflict`
- Decision creation and two updates
- Three alternatives and comparison
- Comment, discussion thread, rationale, and meeting note creation
- Draft to Under Review transition
- Invalid transition rejection
- Reviewer approval and final decision status
- Version list and individual version retrieval
- Employee, manager, and administrator dashboards
- Audit log access
- Decision reports and PDF/Excel exports

## API Checks

- Missing authentication: `401`
- Invalid login: `401`
- Invalid feasibility score: `422`
- Invalid status value: `422`
- Invalid decision transition: `409`
- Missing decision: `404`
- Admin dashboard: `200`
- Python compilation: passed
- Static diagnostics: no errors

## Bugs Found and Fixed

- `BUG-001` High: `/dashboard/admin` passed dependency defaults positionally to `admin_analytics`, causing `500`. Fixed by passing `db` and `user` by name.
- `BUG-002` High: authenticated users could force arbitrary decision statuses. Fixed with role-aware legal transition rules.
- `BUG-003` High: approval completion did not update the decision or create audit records. Fixed to update the decision atomically and write approval and decision audit entries.
- `BUG-004` High: JWT secret was hardcoded. Fixed to load `SECRET_KEY`, algorithm, and expiry from environment settings.
- `BUG-005` Medium: duplicate user creation could expose a database error. Fixed with rollback and `409 Conflict`.
- `BUG-006` High: public registration could create privileged roles. Fixed so only administrators can create Reviewer, Manager, or Administrator users.
- `BUG-007` High: non-administrators could update or delete other users. Fixed with ownership and administrator checks.

## Known Scope

Supporting document upload endpoints are not implemented in the current application, so file-upload cases remain not applicable until that module is added.

The real `.env` must define `SECRET_KEY`; `.env.example` contains placeholders only and no credentials.
