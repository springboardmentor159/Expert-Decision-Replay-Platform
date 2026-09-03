from fastapi import FastAPI

from app.routers.alternatives import router as alternatives_router
from app.routers.users import router as user_router
from app.routers.auth import router as auth_router
from app.routers.decisions import router as decision_router
from app.routers.discussion_threads import router as discussion_threads_router
from app.routers.thread_replies import router as thread_replies_router
from app.routers.meeting_notes import router as meeting_notes_router
from app.routers.decision_rationale import router as rationale_router
from app.routers.comments import router as comments_router
from app.routers.activities import router as activities_router
from app.routers.audit_logs import router as audit_logs_router
from app.routers.dashboard import router as dashboard_router
from app.routers.approvals import router as approvals_router
from app.routers.reports import router as reports_router

app = FastAPI(
    title="Expert Decision Replay Platform"
)


# User Management
app.include_router(user_router)

# Authentication
app.include_router(auth_router)

# Decision Management
app.include_router(decision_router)

# Alternative Analysis
app.include_router(alternatives_router)

# Discussion Module
app.include_router(discussion_threads_router)
app.include_router(thread_replies_router)

# Meeting Notes
app.include_router(meeting_notes_router)

# Decision Rationale
app.include_router(rationale_router)

# Comments
app.include_router(comments_router)

# Dashboard
app.include_router(dashboard_router)

# Activity Logging
app.include_router(activities_router)

# Audit & Compliance
app.include_router(audit_logs_router)

# Approval Workflow
app.include_router(approvals_router)
# Reports and Export Module
app.include_router(reports_router)