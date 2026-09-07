# Expert Decision Replay Platform

A collaborative decision intelligence and audit platform designed to capture, track, analyze, and replay engineering and architectural decisions (ADRs) across their entire lifecycle.

---

## 🚀 Key Features

* **Decision Lifecycle Management**: Create, propose, review, approve, implement, deprecate, or supersede architectural decisions with strict state-transition validations.
* **Alternatives & Trade-Off Matrix**: Evaluate multiple decision options side-by-side with pros, cons, costs, risks, and scoring.
* **Collaboration & Discussions**: Threaded discussions, comments, mentions, and meeting notes attached directly to decision records.
* **Role-Based Access Control (RBAC)**: Fine-grained permissions for Admins, Decision Makers, Contributors, and Viewers.
* **Audit Trail & Governance**: Immutable audit logs capturing every state change, approval, and decision modification.
* **Executive Dashboard & Analytics**: Real-time metrics on decision velocity, status breakdowns, category distributions, and team activity.
* **Reporting & Exports**: Export decision logs and audits to JSON, CSV, and PDF formats.
* **Knowledge Repository**: Searchable, tag-filtered directory of historical organizational decisions.

---

## 🛠️ Tech Stack

### Backend
* **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
* **Database & ORM**: SQLAlchemy, SQLite / PostgreSQL, Alembic migrations
* **Authentication**: JWT (JSON Web Tokens) with Password Hashing (bcrypt)
* **Testing**: Pytest (Lifecycle, Concurrency, RBAC, Validation suites)

### Frontend
* **Framework**: React 18 (SPA)
* **Build Tool**: Vite
* **Icons**: Lucide React
* **Styling**: Vanilla CSS Design System with dark mode, glassmorphism, and responsive layouts

---

## 📂 Project Structure

```text
expert-decision-replay/
├── alembic/              # Database migration scripts
├── app/                  # FastAPI backend application
│   ├── core/             # Configuration, security, and database engine
│   ├── models/           # SQLAlchemy ORM models
│   ├── routers/          # API route endpoints (decisions, auth, reports, etc.)
│   ├── schemas/          # Pydantic validation schemas
│   └── services/         # Business logic and export generators
├── docs/                 # Documentation and matrices
├── frontend/             # React + Vite frontend application
│   └── src/
│       ├── api/          # HTTP API client integration
│       ├── components/   # Reusable UI components
│       ├── context/      # React contexts (Auth, Notifications)
│       └── pages/        # Application view pages
├── tests/                # Automated pytest test suites
└── LICENSE               # MIT License
```

---

## ⚡ Quick Start

### 1. Backend Setup

```bash
# Clone repository and enter project root
git clone https://github.com/springboardmentor159/Expert-Decision-Replay-Platform.git
cd Expert-Decision-Replay-Platform

# Activate your virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# Unix/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations (if applicable)
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```
API Documentation will be accessible at: `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
# In a separate terminal, navigate to the frontend directory
cd frontend

# Install Node dependencies
npm install

# Run Vite dev server
npm run dev
```
Frontend will be accessible at: `http://localhost:5173`

### 3. Running Tests

```bash
pytest
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
