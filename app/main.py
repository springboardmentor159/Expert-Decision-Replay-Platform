from fastapi import FastAPI

from app.routers.users import router as user_router
from app.routers.auth import router as auth_router
from app.routers.decisions import router as decision_router
from app.routers.audit_logs import router as audit_log_router
from app.routers import alternatives
from app.routers import meeting_notes
from app.routers import decision_rationale
from app.routers import tags
from app.routers import decision_tags
from app.routers import activities
from app.routers.dashboard import router as dashboard_router
from app.routers.approvals import router as approval_router
from app.routers.activities import router as activities_router
from app.routers.comments import (
    decision_comments_router,
    comments_router
)


app = FastAPI(
    title="Expert Decision Replay Platform"
)


app.include_router(user_router)

app.include_router(auth_router)

app.include_router(decision_router)

app.include_router(alternatives.router)

app.include_router(decision_comments_router)

app.include_router(comments_router)



app.include_router(meeting_notes.router)
app.include_router(decision_rationale.router)
app.include_router(tags.router)
app.include_router(decision_tags.router)
app.include_router(approval_router)
app.include_router(dashboard_router)
app.include_router(activities.router)
app.include_router(audit_log_router)
