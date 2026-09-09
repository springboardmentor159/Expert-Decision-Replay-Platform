# Expert Decision Replay Platform — Frontend (Sprint 14)

A React (Vite) frontend that implements the full UI from the Sprint 14 brief and talks
to your existing FastAPI backend (`Expert-Decision-Replay-Platform/app`) over REST.

## What's included

- Login / Registration (JWT)
- Role-based navigation and route guards (Employee, Reviewer, Manager, Administrator)
- Role dashboards (Employee / Reviewer / Manager / Admin)
- Decision list (filter, sort, paginate), create, and detail (tabs: Overview, Alternatives,
  Discussions, Approval, History)
- Alternatives: add / edit / compare
- Discussions: comments, threads + replies, meeting notes
- Approval workflow: assign reviewer, approve/reject, pending-review queue
- Knowledge Repository (search + filters)
- Version History / Timeline
- Audit & Activity (Administrator only): audit logs, security logs, access logs
- Reports (Decisions / Approvals / Teams / Audit) with PDF & Excel export
- User management (Administrator only)
- Centralized API layer with 401/403/404/422/500 handling, loading/empty/error states
  on every page, and client-side form validation

## 1. Prerequisites

- Node.js 18+ and npm
- Your FastAPI backend running locally (see step 3)

## 2. Install & configure

```bash
cd frontend
npm install
cp .env.example .env
```

Open `.env` and confirm `VITE_API_BASE_URL` points at your backend, e.g.:

```
VITE_API_BASE_URL=http://localhost:8000
```

## 3. Run the backend with CORS enabled

The backend didn't have CORS middleware, which blocks browser requests from a
different origin (the frontend dev server runs on `http://localhost:5173`).
A patch has already been applied to
`Expert-Decision-Replay-Platform/app/main.py` adding:

```python
from fastapi.middleware.cors import CORSMiddleware
...
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

If you deploy the frontend somewhere else later, add that URL to `allow_origins`.

Start the backend as you normally do, e.g.:

```bash
cd Expert-Decision-Replay-Platform
uvicorn main:app --reload
```

Confirm it's up at `http://localhost:8000/docs`.

## 4. Run the frontend

```bash
cd frontend
npm run dev
```

Open the URL Vite prints (typically `http://localhost:5173`).

## 5. Try the end-to-end flow

1. Register a user with role **Employee** (and, separately, one each for
   **Reviewer**, **Manager**, **Administrator** — the backend has no self-serve
   role escalation, so create one of each to test all dashboards, or have an
   Administrator change a user's role from **User Management**).
2. Log in as the Employee → create a decision → add alternatives → compare them →
   start a discussion → submit the decision for review.
3. Log in as a Manager (or Administrator) → open the decision → **Approval** tab →
   assign it to your Reviewer.
4. Log in as the Reviewer → **Assigned Reviews** → approve or reject.
5. Back as the Employee/Manager, check the decision's **History** tab for the
   version/timeline entries, and the **Knowledge Repository** to search for it.
6. As Administrator, check **Audit Logs** and **Reports** (try PDF/Excel export).

## Project structure

```
src/
  api/          Centralized service layer — one file per resource, all HTTP calls live here
  components/   Reusable UI (Button, Input, Table, Modal, Badge, layout, route guards)
  context/      AuthContext (JWT storage, current-user profile)
  pages/        One folder per feature area (auth, dashboard, decisions, alternatives,
                discussions, approvals, repository, audit, reports, users)
  utils/        Formatting helpers + role/navigation config
```

## Notes on how this maps to your backend

- Login calls `POST /users/login` as `application/x-www-form-urlencoded`
  (`username` + `password`), matching `OAuth2PasswordRequestForm`.
- There's no `/users/me` endpoint, so after login the frontend decodes the JWT's
  `sub` claim (the user id) and calls `GET /users/{id}` to load the profile —
  which is allowed because a user can always read their own record.
- The Reviewer dashboard has no dedicated `/dashboard/reviewer` backend route, so
  it's built from `GET /approvals/pending` (the reviewer's own queue).
- Feasibility score is constrained to 1–5 client-side (matching the backend's
  `Field(..., ge=1, le=5)`), and risk level is restricted to the same enum
  (`Low` / `Medium` / `High` / `Critical`).
- Decision status transitions are only exposed where the backend allows them
  (`Draft → Under Review`, `Approved|Rejected → Archived`).

## Building for production

```bash
npm run build
```

Output goes to `dist/`. Serve it with any static host, and set
`VITE_API_BASE_URL` (at build time, via `.env.production` or your CI) to your
deployed backend URL — then add that origin to the backend's CORS
`allow_origins` list.
