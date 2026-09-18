# Expert Decision Replay Platform

A full-stack decision lifecycle platform for capturing organizational decisions, evaluating alternatives, collaborating through discussions, routing decisions through approval stages, and preserving an auditable history for future replay.

## Stack

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, Alembic, JWT authentication
- **Frontend:** React, TypeScript, Vite, React Router, Axios, Lucide icons
- **Reporting:** PDF and Excel exports

## Core workflow

1. Register an account (public registration creates an Employee account).
2. Sign in and receive a JWT session.
3. Create a decision as a draft.
4. Add alternatives and compare cost, feasibility, and risk.
5. Start discussions and comments.
6. Submit a draft for review.
7. A Manager assigns approval stages to a Reviewer/Manager.
8. The assigned Reviewer starts and completes the review.
9. The final Manager/Admin approval completes or rejects the decision.
10. Review version history, activity, audit information, repository records, and reports.
11. Export authorized reports to PDF or Excel.

## Roles

| Role | Primary capabilities |
|---|---|
| Employee | Create/manage own draft decisions, alternatives, discussions, repository access |
| Reviewer | Assigned approval reviews, decision collaboration, repository and reports |
| Manager | Department oversight, approval assignment/completion, team reports |
| Administrator | Platform oversight, user management, audit reports, all reporting capabilities |

## Project structure

```text
app/                 FastAPI application
app/routers/         REST API endpoints
app/services/        Audit, activity, and reporting services
app/models/          SQLAlchemy models
app/schemas/         Pydantic request/response schemas
alembic/              Database migrations
frontend/src/        React application
frontend/src/pages/  Application screens
frontend/src/services Centralized API service modules
```

## Backend setup

Create a virtual environment and install dependencies:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `.env` from `.env.example` and set your PostgreSQL connection and JWT secret. **Never commit `.env`.**

Run migrations:

```powershell
alembic upgrade head
```

Start the API:

```powershell
uvicorn app.main:app --reload
```

API documentation is available at `http://127.0.0.1:8000/docs` while the development server is running.

## Frontend setup

From `frontend`:

```powershell
npm install
npm run dev
```

Set `VITE_API_BASE_URL` in `frontend/.env` to the backend URL, for example:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Build for production:

```powershell
npm run build
```

## Security notes

- Public registration creates only Employee accounts.
- Privileged roles are managed through authenticated administrator functionality.
- Protected API endpoints validate the JWT and enforce role/ownership rules.
- Audit records are generated for important decision, approval, user, alternative, and comment operations.
- Do not commit passwords, JWT secrets, database credentials, API keys, `.env` files, `node_modules`, or build output.

## Database migrations

Check the migration state with:

```powershell
alembic current
alembic heads
```

Apply pending migrations with:

```powershell
alembic upgrade head
```

## Validation checklist

Before submission, verify:

- Registration and invalid registration validation
- Valid and invalid login
- Logout and expired-session handling
- Employee, Reviewer, Manager, and Administrator dashboards
- Decision create/edit/delete permissions
- Decision submission and status transitions
- Alternative create/edit/delete/compare and feasibility validation
- Discussion/comment create/edit/delete
- Reviewer and Manager approval workflow
- Version history and comparison
- Repository search, filters, sorting, and pagination
- Activity and Administrator-only audit reporting
- Decision, approval, and team reports
- PDF and Excel exports with selected filters
- Loading, empty, validation, 401/403/404/422/500 states
- Desktop and mobile responsive layouts

## License

MIT License. See `LICENSE`.
