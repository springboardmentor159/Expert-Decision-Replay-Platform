# Expert Decision Replay Platform — Project Handover Document

## 1. Project Overview & Current State
The **Expert Decision Replay Platform** is a full-stack enterprise decision governance, versioning, and compliance audit platform. 

### Key Accomplishments
- **Backend (FastAPI / SQLAlchemy / PostgreSQL / Alembic)**:
  - 12 Database models (`users`, `decisions`, `decision_versions`, `alternatives`, `comments`, `discussion_threads`, `meeting_notes`, `documents`, `audit_log`, `activity_log`, `security_logs`, `access_logs`).
  - Full RBAC supporting **Employee**, **Reviewer**, **Manager**, and **Administrator**.
  - Decision snapshot versioning engine (v1, v2, v3...) for historical decision replay.
  - Alternatives matrix comparison (`GET /decisions/{id}/alternatives/compare`).
  - Multi-channel collaboration (comments, discussion threads with replies, meeting notes).
  - Reporting & Export engine: 4 JSON endpoints + 4 PDF exports (`reportlab`) + 4 Excel exports (`openpyxl`).
  - Document uploads, downloads, and association with decisions.
  - Comprehensive automated test suite with over **850+ passing tests**.

- **Frontend (React 19 / Vite / Apple Design System)**:
  - Responsive web application located in `frontend/`.
  - Adherence to [`DESIGN.md`](file:///c:/Users/Bhargav/Desktop/expert-decision-replay/DESIGN.md) (SF Pro/Inter typography, Action Blue `#0066cc`, Parchment `#f5f5f7`, Dark Tiles `#272729`, Pill CTAs, active scale-down micro-interactions).
  - Full JWT authentication, localStorage token management, 401 redirect intercepts, and role-based route/action gates.
  - Complete shared component library (`Button`, `Badge`, `Alert`, `Modal`, `Table`, `Pagination`, `FilterBar`, `SearchInput`, `FormField`, `LoadingSpinner`, `Skeleton`, `EmptyState`).
  - Dedicated pages: `LoginPage`, `DashboardPage`, `DecisionsPage`, `ComponentShowcasePage`, `UnauthorizedPage`, `NotFoundPage`.

---

## 2. Quick Start & Execution Commands

### Running Backend API
```powershell
# Activate Python virtualenv
.\venv\Scripts\Activate.ps1

# Run database migrations
alembic upgrade head

# Start FastAPI server (Port 8000)
uvicorn app.main:app --port 8000 --reload
```
- Swagger API Docs: `http://localhost:8000/docs`
- Root Healthcheck: `http://localhost:8000/`

### Running React Frontend
```powershell
cd frontend
npm install
npm run dev
```
- Web Application: `http://localhost:5173/`

### Running Automated Test Suite
```powershell
# Backend Pytest Suite
pytest -q

# Frontend Production Build Verification
cd frontend
npm run build
```

---

## 3. Demo User Accounts & Credentials

| Role | Email | Password | Allowed Capabilities |
|---|---|---|---|
| **Employee** | `employee@example.com` | `password1234` | Create decisions, add alternatives, join discussions, view personal dashboard |
| **Reviewer** | `reviewer@example.com` | `password1234` | All Employee actions + Review and endorse decision proposals |
| **Manager** | `manager@example.com` | `password1234` | All Reviewer actions + Approve/Reject decisions, view Manager stats & org reports |
| **Administrator** | `admin@example.com` | `password1234` | Full system access + User management, moderation, full audit & security logs |

---

## 4. Key Project Files Reference

- [`Description.txt`](file:///c:/Users/Bhargav/Desktop/expert-decision-replay/Description.txt) — Comprehensive architectural and operational description of the platform.
- [`task.md`](file:///c:/Users/Bhargav/Desktop/expert-decision-replay/task.md) — Chronological progress tracker across all development sprints.
- [`DESIGN.md`](file:///c:/Users/Bhargav/Desktop/expert-decision-replay/DESIGN.md) — Apple design system specification for UI tokens and styles.
- [`app/main.py`](file:///c:/Users/Bhargav/Desktop/expert-decision-replay/app/main.py) — FastAPI main entry point and CORS configuration.
- [`frontend/src/App.jsx`](file:///c:/Users/Bhargav/Desktop/expert-decision-replay/frontend/src/App.jsx) — React routing and protected route architecture.
- [`frontend/src/context/AuthContext.jsx`](file:///c:/Users/Bhargav/Desktop/expert-decision-replay/frontend/src/context/AuthContext.jsx) — Auth state, JWT management, and role helpers.
- [`frontend/src/pages/ComponentShowcasePage.jsx`](file:///c:/Users/Bhargav/Desktop/expert-decision-replay/frontend/src/pages/ComponentShowcasePage.jsx) — Live playground demonstrating all UI components.

---

## 5. Next Steps for Incoming Engineers
1. Extend the frontend decisions view to support full decision detail inspection with tabs for Alternatives comparison, Discussions, Meeting Notes, and Document Attachments.
2. Implement front-end reporting dashboards rendering dynamic charts for Manager and Admin statistics.
3. Hook up document file upload component directly to `POST /decisions/{id}/documents`.
