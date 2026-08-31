from fastapi import FastAPI

from app.routers import (
    auth,
    user,
    decision,
    alternative,
    comment,
    discussion_thread,
    meeting_notes,
    rationale,
    tags,
    timeline,
    decision_version,
    dashboard,
    activities,
    audit_logs,
)

app = FastAPI(
    title="Expert Decision Replay Platform"
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(decision.router)
app.include_router(alternative.router)
app.include_router(comment.router)
app.include_router(discussion_thread.router)
app.include_router(meeting_notes.router)
app.include_router(rationale.router)
app.include_router(tags.router)
app.include_router(timeline.router)
app.include_router(decision_version.router)
app.include_router(dashboard.router)
app.include_router(activities.router)
app.include_router(audit_logs.router)
@app.get("/")
def root():
    return {
        "message": "Expert Decision Replay Platform API is running"
    }