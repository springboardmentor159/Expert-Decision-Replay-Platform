# Expert Decision Replay Platform 🏛️⚡

> **An Audit-Grade Institutional Knowledge Engine & Architecture Decision Governance System**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-5.0-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 📌 Table of Contents
1. [What is the Project?](#-what-is-the-project)
2. [What Does the Platform Do?](#-what-does-the-platform-do)
3. [End-to-End Workflow: Step-by-Step (Employee &rarr; Admin)](#-end-to-end-workflow-step-by-step-employee--admin)
   - [Step 1: Employee (Contributor)](#1-employee-contributor---authoring--proposal)
   - [Step 2: Reviewer (Peer Lead / Principal Architect)](#2-reviewer-peer-lead--principal-architect---technical-evaluation)
   - [Step 3: Manager (VP / Director of Architecture)](#3-manager-vp--director---operational-sign-off)
   - [Step 4: Administrator (Executive / Governance)](#4-administrator-executive--governance---system-management)
4. [Key Features & Capabilities](#-key-features--capabilities)
5. [Tech Stack](#-tech-stack)
6. [Local Installation & Setup](#-local-installation--setup)
7. [Pre-Seeded Demo Credentials](#-pre-seeded-demo-credentials)
8. [Automated Testing Suite](#-automated-testing-suite)
9. [API Endpoints & Documentation](#-api-endpoints--documentation)

---

## 💡 What is the Project?

In fast-moving software and infrastructure engineering, critical architectural decisions (e.g., choosing database engines, adopting event streaming, migrating to microservices, or selecting cloud providers) often get buried in ad-hoc Slack threads, Zoom calls, or fleeting meeting notes. When senior engineers leave, **tribal knowledge is lost forever**, and teams repeatedly question *"Why did we build it this way?"*

**Expert Decision Replay** solves this by treating Architectural Decision Records (ADRs) as **living, auditable, and replayable assets**:
- It captures not just the final choice, but the **entire deliberation journey**—every alternative evaluated, trade-off weighed, cost analyzed, and peer critique raised.
- It provides an **Interactive Decision Replay Scrubber** that functions like a time machine, animating the progression from initial problem formulation to final director sign-off.
- It enforces **Multi-Level Sequential Governance (ARB)** to guarantee that proposals undergo rigorous peer review and managerial authorization before entering implementation.

---

## 🎯 What Does the Platform Do?

1. **Structured Decision Formulation**: Guides authors through context definition, consequences, scope, tags, and category classification.
2. **Candidate Alternatives & Trade-Off Benchmarking**: Side-by-side matrices comparing feasibility score, financial cost (in ₹), risk assessments (Low, Medium, High, Critical), pros, and cons.
3. **Interactive Decision Replay**: Step-by-step visual scrubbing engine displaying who approved what, when decisions shifted states, and how consensus crystallized over time.
4. **Institutional Knowledge Repository**: Centralized, searchable repository accessible across the organization to prevent duplicate evaluations and accelerate onboarding.
5. **Real-Time Threaded Discussions**: Context-bound comment threads and meeting notes attached directly to decision records.
6. **Executive Analytics & Governance Dashboards**: Real-time charts detailing decision velocity, approval stage bottlenecks, and category distributions.
7. **Immutable Audit Trails**: Full cryptographic logging of every status transition, alternative selection, and permission check.

---

## 🪜 End-to-End Workflow: Step-by-Step (Employee &rarr; Admin)

The platform implements a strict **Role-Based Access Control (RBAC)** architecture that reflects real-world engineering governance:

```
┌─────────────────┐        ┌──────────────────┐        ┌─────────────────┐        ┌──────────────────┐
│ 1. Employee     │ ─────> │ 2. Reviewer      │ ─────> │ 3. Manager      │ ─────> │ 4. Administrator │
│ (Draft & Submit)│        │ (Peer ARB Gate 1)│        │ (Exec ARB Gate 2)│       │ (Audit & Manage) │
└─────────────────┘        └──────────────────┘        └─────────────────┘        └──────────────────┘
```

---

### 1. Employee (Contributor) - *Authoring & Proposal*
* **Access**: Can access the Knowledge Repository, Personal Decisions, and Profile.
* **Actions**:
  1. **Log in** with Employee credentials.
  2. Click **`+ New Decision`** to initiate an Architectural Decision Record (ADR).
  3. Fill in title, context, architectural impact, urgency, and category.
  4. **Add Alternatives**: Propose 2 or more options (e.g., *Option A: Apache Kafka* vs. *Option B: RabbitMQ* vs. *Option C: AWS SQS*), detailing:
     - Projected Cost (₹)
     - Feasibility Score (0–100%)
     - Risk Level (`Low`, `Medium`, `High`, `Critical`)
     - Key Pros and Cons
  5. Upload technical diagrams or specification attachments (`.png`, `.pdf`, `.docx`).
  6. Submit the decision into **`In Review`** status.
  7. Participate in threaded discussions answering peer questions.

---

### 2. Reviewer (Peer Lead / Principal Architect) - *Technical Evaluation*
* **Access**: All Employee permissions + Reviewer Queue & Approval Gate 1.
* **Actions**:
  1. **Log in** with Reviewer credentials.
  2. Navigate to pending decisions requiring technical scrutiny.
  3. Review the candidate alternatives side-by-side in the **Trade-Off Matrix**.
  4. Post technical feedback, questions, or clarification requests in the threaded discussion.
  5. Vote on alternatives and submit Gate 1 peer evaluation:
     - **Approve**: Advances decision to Managerial review.
     - **Request Revisions**: Sends the decision back to the author with feedback.

---

### 3. Manager (VP / Director) - *Operational Sign-Off*
* **Access**: Reviewer permissions + Executive Authorization Gate 2.
* **Actions**:
  1. **Log in** with Manager credentials.
  2. Access pending decisions that have cleared Gate 1 peer review.
  3. Evaluate budgetary feasibility, cross-team impact, staffing requirements, and compliance.
  4. Select and designate the **Official Chosen Alternative** (highlighted with a green badge in the decision record).
  5. Issue formal sign-off:
     - **Approved**: Transition to active implementation phase.
     - **Rejected**: Closes the decision with recorded rationale.
  6. Monitor the **Replay Scrubber** to inspect the consensus history.

---

### 4. Administrator (Executive / Governance) - *System Management*
* **Access**: Unrestricted global platform administration.
* **Actions**:
  1. **Log in** with Administrator credentials.
  2. Open the **Admin Management Panel**:
     - **User Management**: Add, edit, deactivate users, and adjust RBAC roles (`Employee`, `Reviewer`, `Manager`, `Administrator`).
     - **Organization Control**: Configure organizations and teams.
     - **Executive Analytics**: Interactive charts visualizing decision volume, status distribution, approval velocity, and cost allocations.
     - **Audit Logs**: Immutable records of every system event with IP address, user timestamp, and payload diffs.
  3. Override, archive, or mark decisions as **Superseded** or **Deprecated** when architectures evolve.

---

## 🌟 Key Features & Capabilities

| Feature | Description |
| :--- | :--- |
| **Interactive Replay Scrubber** | Step-by-step playback slider demonstrating decision timeline evolution from draft to approval. |
| **Trade-Off Matrix** | Side-by-side comparison of candidate alternatives displaying feasibility, cost in ₹, risk levels, and chosen badge. |
| **Multi-Tier ARB Pipeline** | Two-stage approval gates (Peer Lead Gate 1 &rarr; Director Gate 2) preventing unilateral decisions. |
| **Interactive Analytics** | Real-time SVG distribution charts displaying status splits, category breakdowns, and team velocity. |
| **Audit Logs & Governance** | Immutable logging of every update with cryptographic Argon2id password hashing and session safety. |
| **Attachment Vault** | Secure technical file upload and preview system for specs and architecture diagrams. |
| **Knowledge Repository** | Full-text search and multi-criteria tag filter for historical decisions. |
| **Dark & Light Themes** | Complete vanilla CSS design system supporting high-contrast dark and light modes. |

---

## 🛠️ Tech Stack

### Backend
* **Language & Runtime**: Python 3.10+
* **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous REST API)
* **Database & ORM**: PostgreSQL / SQLite with SQLAlchemy 2.0
* **Schema Validation**: Pydantic v2
* **Security & Auth**: JWT (JSON Web Tokens), OAuth2 password bearer, Argon2id & Bcrypt hashing
* **Test Suite**: Pytest (120+ comprehensive tests across auth, RBAC, lifecycle, concurrency, and audits)

### Frontend
* **UI Framework**: React 18 (Single Page Application)
* **Build System**: Vite 5.x
* **Icons**: Lucide React
* **Styling**: Tailored Vanilla CSS Design System with custom tokens, responsive cards, glassmorphic accents, and zero heavyweight CSS dependencies.

---

## 💻 Local Installation & Setup

### Prerequisites
* **Python**: Version 3.10 or higher
* **Node.js**: Version 18 or higher (with `npm`)
* **Git**: Installed and configured

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/springboardmentor159/Expert-Decision-Replay-Platform.git
cd Expert-Decision-Replay-Platform
git checkout Ayush
```

---

### Step 2: Backend Setup
Open a terminal in the project root:

```bash
# 1. Create and activate a Python virtual environment
# Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux:
python3 -m venv venv
source venv/bin/activate

# 2. Install backend dependencies
pip install -r requirements.txt

# 3. Initialize & seed the database with pristine demo data
python scripts/seed_db.py

# 4. Start the FastAPI backend server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend will be running at: **`http://127.0.0.1:8000`**  
Interactive API Documentation (Swagger): **`http://127.0.0.1:8000/docs`**

---

### Step 3: Frontend Setup
Open a **second terminal** window:

```bash
# 1. Navigate to the frontend directory
cd frontend

# 2. Install Node dependencies
npm install

# 3. Start the Vite development server
npm run dev
```

The frontend web app will be running at: **`http://localhost:5173`**

---

## 🔑 Pre-Seeded Demo Credentials

The database seeding script (`scripts/seed_db.py`) pre-configures accounts for each role:

| Role | Email Address | Password | Role Description |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@example.com` | `password123` | CIO / Executive with global admin & audit rights |
| **Manager** | `manager@example.com` | `password123` | VP of Architecture with Gate 2 sign-off rights |
| **Reviewer** | `reviewer@example.com` | `password123` | Principal Architect with Gate 1 review rights |
| **Employee** | `employee@example.com` | `password123` | Software Engineer / ADR Author |

> 💡 **Tip**: On the Login screen, use the **Quick Demo Accounts (1-Click Fill)** buttons to instantly populate any of these credentials with a single click.

---

## 🧪 Automated Testing Suite

To run the backend test suite verifying RBAC permissions, decision lifecycle state-machines, concurrency, and audit logs:

```bash
# From project root with virtual environment activated:
pytest -v
```

To validate the production bundle build for the frontend:
```bash
cd frontend
npm run build
```

---

## 📡 API Endpoints & Documentation

Once the backend is running, explore all endpoints via interactive documentation:
* **Swagger UI**: `http://localhost:8000/docs`
* **ReDoc**: `http://localhost:8000/redoc`

### Core Route Groups:
* `POST /auth/login` - Authenticate and obtain JWT access token.
* `POST /auth/register` - Register a new organizational user.
* `GET /decisions/` - List and filter decisions with pagination.
* `POST /decisions/` - Create a new architecture decision.
* `GET /decisions/{id}/replay` - Retrieve chronologically sequenced replay snapshots.
* `POST /decisions/{id}/alternatives` - Attach candidate alternatives with trade-offs.
* `POST /decisions/{id}/approvals` - Submit Gate 1 / Gate 2 approval votes.
* `GET /admin/analytics` - Retrieve executive governance metrics and charts.
* `GET /admin/audit-logs` - Inspect immutable system governance audit trail.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
