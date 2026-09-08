from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    users,
    login,
    decisions,
    alternatives,
    comments,
    tags,
    analytics,
    audit_logs,
    reports,
    approvals
)

from app.routers.dashboard import router as dashboard_router


app = FastAPI(
    title="Expert Decision Replay Platform",
    description="API for managing decisions, alternatives, comments, tags, dashboards and analytics",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(login.router)
app.include_router(decisions.router)
app.include_router(alternatives.router)
app.include_router(comments.router)
app.include_router(tags.router)
app.include_router(audit_logs.router)
app.include_router(approvals.router)

# Dashboard routes
app.include_router(dashboard_router)

# Analytics routes
app.include_router(analytics.router)
app.include_router(reports.router)


@app.get("/")
def root():
    return {
        "message": "Expert Decision Replay Platform API is running"
    }
