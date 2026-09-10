# Expert Decision Replay Platform

Enterprise Architecture Decision Records (ADR), Multi-Level Review & Approval Workflows, Alternative Comparison Matrix, Knowledge Repository Search, Compliance Auditing, and Centralized PDF/Excel Reporting.

---

## Architecture Overview

- **Backend**: FastAPI (Python 3.10+), SQLAlchemy ORM, Alembic Migrations, SQLite / PostgreSQL, JWT Authentication.
- **Frontend**: React 18/19, Vite, Modular Vanilla CSS Design System (no Tailwind per guidelines), Axios centralized API client, Lucide icons.

---

## Getting Started

### 1. Backend Setup & Startup

1. **Activate Virtual Environment**:
   ```cmd
   venv\Scripts\activate
   ```

2. **Install Backend Dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

3. **Run Database Migrations & Seed Demo Users**:
   ```cmd
   alembic upgrade head
   python seed_demo_users.py
   ```

4. **Start the FastAPI Backend Server** (Port 8000):
   ```cmd
   uvicorn app.main:app --reload --port 8000
   ```
   - Swagger Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - OpenAPI Specification: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

### 2. Frontend Setup & Startup

1. **Navigate to the frontend directory**:
   ```cmd
   cd frontend
   ```

2. **Install Node Dependencies**:
   ```cmd
   npm install
   ```

3. **Start the Vite Development Server** (Port 5173):
   ```cmd
   npm run dev
   ```
   - Application Web UI: [http://localhost:5173](http://localhost:5173)

4. **Build for Production**:
   ```cmd
   npm run build
   ```

---

## Pre-Configured Demo User Accounts

The login interface includes 1-click quick-fill buttons for each role:

| Role | Email | Password | Department | Primary Permissions |
| :--- | :--- | :--- | :--- | :--- |
| **Employee** | `employee@example.com` | `Password123!` | Engineering | Author decisions, add alternatives, participate in discussions, submit for review. |
| **Reviewer** | `reviewer@example.com` | `Password123!` | Engineering | Review assigned proposals, compare alternatives side-by-side, approve/reject. |
| **Manager** | `manager@example.com` | `Password123!` | Engineering | Team decisions dashboard, pending approvals, team reports. |
| **Administrator** | `admin@example.com` | `Password123!` | Executive | Full tenant administration, user management, immutable audit logs, system telemetry. |

---

## End-to-End Workflow

1. **Sign in** with an Employee account (or register a new user).
2. **Author a new architecture decision** with problem statement, criteria, and tags.
3. **Add alternatives** with feasibility scores (1-5), estimated cost, pros/cons, and risk ratings.
4. **Compare alternatives** side-by-side to evaluate architectural trade-offs.
5. **Start discussions**, post comments, and record meeting notes.
6. **Submit the decision for review** to route it to a technical reviewer.
7. **Sign in as Reviewer or Manager** to inspect the review queue and **Approve** or **Reject** with comments.
8. **View updated version history and sequential audit timeline**.
9. **Search decisions** in the Knowledge Repository with keyword, tag, and status filters.
10. **Generate reports** and export audit-ready **PDF** or **Excel** files.
