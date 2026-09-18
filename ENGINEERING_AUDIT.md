# Sprint 14 Engineering Audit

This repository was reviewed against the supplied Sprint 14 mentor requirements before packaging.

## Implemented in this revision

- Added a dedicated public registration endpoint that always creates an Employee account.
- Restricted privileged user creation, user listing, role changes, and deletion to authenticated administrators (with department-scoped user visibility for managers).
- Added administrator User Management UI with search, create, edit, role management, and protected deletion.
- Added a real Reviewer dashboard API and frontend dashboard handling.
- Added role-aware application navigation, including review, approval, activity, reporting, and administrator user-management entry points.
- Added approval-stage assignment UI for managers/administrators.
- Added sequential approval enforcement and role-aware approval actions.
- Added approval audit/activity records.
- Added decision ownership/status permissions, draft deletion, validated status transitions, and version records for create/submit/status changes.
- Added decision activity records for update/submit/archive/delete operations.
- Restricted alternative mutation to permitted draft owners/administrators.
- Fixed report summary filtering so status-filtered decision reports use matching summary totals.
- Restricted team reports to Manager/Administrator roles.
- Removed frontend debug logging.
- Added/normalized frontend TypeScript project configuration.
- Replaced the oversized/freezed dependency list with the project's direct runtime dependencies.
- Strengthened `.gitignore` for environment files, frontend build/dependency directories, and generated local reports.
- Rebuilt the README with setup, architecture, roles, workflow, security, migration, and acceptance guidance.
- Removed generated Python cache files from the deliverable.

## Static verification

- Python source compilation: **passed** with `python -m compileall app alembic`.
- Migration head inspection: **a00ca0879a09**.
- Frontend TypeScript syntax scan of changed files: **passed** (no parser/JSX syntax errors detected).
- Repository source scan for `console.*`, TODO/FIXME, and debugger statements: **clean**.

## Live verification required on the developer machine

The frontend dependencies and PostgreSQL credentials are intentionally not packaged. After extracting the project, run the normal frontend install/build and execute the full browser E2E flow against the configured database. This is necessary to verify the real environment, seeded users, and current database state.

Recommended final checks:

```powershell
# Backend
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run build
npm run dev
```

Then verify the complete mentor flow: registration → login → dashboard → decision creation → alternatives → comparison → discussion → submission → reviewer action → manager approval/rejection → status → version history → audit/activity → repository → reports → PDF/Excel.
