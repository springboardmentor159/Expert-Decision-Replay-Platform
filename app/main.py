from fastapi import FastAPI
from fastapi.security import HTTPBearer

from app.core.config import settings
from app.routers.user import router as user_router
from app.routers.auth import router as auth_router
from app.routers.decision import router as decision_router
from app.routers.alternative import router as alternative_router
from app.routers.comment import router as comment_router
from app.routers.discussion_thread import router as discussion_thread_router
from app.routers.meeting_note import router as meeting_note_router
from app.routers.tag import router as tag_router
from app.routers.dashboard import router as dashboard_router
from app.routers.approval import router as approval_router
from app.routers.activity import router as activity_router
from app.routers.audit import router as audit_router
app = FastAPI(
    title=settings.app_name,
    version="1.0.0"
)

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(decision_router)
app.include_router(alternative_router)
app.include_router(comment_router)
app.include_router(discussion_thread_router)
app.include_router(meeting_note_router)
app.include_router(tag_router)
app.include_router(dashboard_router)
app.include_router(approval_router)
app.include_router(activity_router)
app.include_router(audit_router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name
    }