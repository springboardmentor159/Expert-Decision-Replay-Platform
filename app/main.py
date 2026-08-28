from fastapi import FastAPI

from app.core.config import settings

from app.routers.users import router as user_router
from app.routers.auth import router as auth_router
from app.routers.decisions import router as decision_router
from app.routers.alternatives import router as alternative_router
from app.routers.comments import router as comment_router
from app.routers.threads import router as thread_router
from app.routers.meeting_notes import router as meeting_note_router
from app.routers.tags import router as tag_router
from app.routers.audit import router as audit_router
from app.routers.approvals import router as approvals_router
from app.routers.dashboard import router as dashboard_router
from app.routers.activities import router as activities_router
from app.routers.organizations import router as organization_router


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
)


# Authentication APIs
app.include_router(auth_router)

# User Management APIs
app.include_router(user_router)

# Decision Management APIs
app.include_router(decision_router)

# Alternative Analysis APIs
app.include_router(alternative_router)

# Comment APIs
app.include_router(comment_router)

# Thread APIs
app.include_router(thread_router)

# Meeting Note APIs
app.include_router(meeting_note_router)

# Tag Management APIs
app.include_router(tag_router)

app.include_router(audit_router)

app.include_router(approvals_router)

app.include_router(dashboard_router)

app.include_router(activities_router)

app.include_router(organization_router)

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}"
    }