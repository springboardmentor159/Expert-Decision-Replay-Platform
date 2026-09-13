\# Expert Decision Replay Platform



A FastAPI-based platform for creating, discussing, reviewing, approving, auditing, and reporting organizational decisions.



\## Features



\- JWT-based authentication

\- Role-Based Access Control (RBAC)

\- User management

\- Decision management

\- Decision alternatives

\- Alternative comparison

\- Feasibility and risk assessment

\- Comments and discussion threads

\- Meeting notes

\- Decision rationale

\- Approval workflow

\- Activity logging

\- Audit and compliance logs

\- Decision version history

\- Employee, Manager, and Administrator dashboards

\- Decision, approval, team, and audit reports

\- PDF and Excel report exports

\- Search, filtering, pagination, and sorting

\- PostgreSQL database

\- Docker and Docker Compose support



\## Technology Stack



\- Python 3.13

\- FastAPI

\- SQLAlchemy

\- PostgreSQL

\- Alembic

\- Pydantic

\- JWT Authentication

\- Passlib / bcrypt

\- ReportLab

\- OpenPyXL

\- Docker



\## Project Structure



```text

Expert-Decision-Replay-Platform/

├── app/

│   ├── models/

│   ├── schemas/

│   ├── routers/

│   ├── services/

│   └── main.py

├── alembic/

├── Dockerfile

├── docker-compose.yml

├── .dockerignore

├── .env.example

├── .gitignore

├── alembic.ini

├── requirements.txt

└── README.md

