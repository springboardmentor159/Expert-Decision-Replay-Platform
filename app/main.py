from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.routers.activities import router as activities_router
from app.routers.access_log import router as access_log_router
from app.routers.alternative import alternatives_router, router as alternative_router
from app.routers.audit import audit_logs_router, router as audit_router
from app.routers.comment import comments_router, router as comment_router
from app.routers.dashboard import router as dashboard_router
from app.routers.decision import router as decision_router
from app.routers.discussion_thread import threads_router, router as thread_router
from app.routers.meeting_note import meeting_notes_router, router as meeting_note_router
from app.routers.security import router as security_router
from app.routers.user import router as user_router

app = FastAPI(
    title="Expert Decision Replay Platform"
)

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(decision_router)
app.include_router(alternative_router)
app.include_router(alternatives_router)
app.include_router(comment_router)
app.include_router(comments_router)
app.include_router(dashboard_router)
app.include_router(thread_router)
app.include_router(threads_router)
app.include_router(meeting_note_router)
app.include_router(meeting_notes_router)
app.include_router(activities_router)
app.include_router(audit_router)
app.include_router(audit_logs_router)
app.include_router(security_router)
app.include_router(access_log_router)


@app.get("/")
def root():
    return {"message": "API is running"}