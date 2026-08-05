# Expert Decision Replay Platform

FastAPI application with PostgreSQL, SQLAlchemy, and Alembic migrations.

## Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL server installed and running on port 5432
- Database `expert_decision_replay` created in PostgreSQL

### Installation & Virtual Environment

1. Activate virtual environment:
   ```cmd
   venv\Scripts\activate
   ```

2. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```

### Database Setup & Migrations

Run database migrations using Alembic:
```cmd
alembic upgrade head
```

### Running the Application

Start the Uvicorn development server:
```cmd
uvicorn app.main:app --reload
```

Interactive API documentation available at:
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
