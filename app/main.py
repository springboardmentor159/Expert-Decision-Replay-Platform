from fastapi import FastAPI

from app.routers import (
    tags,
    user,
    decision,
    alternative,
    auth,
    comment,
    discussion_thread,
    decision_version,
    meeting_notes,
    rationale,
    
)

app = FastAPI(title="Expert Decision Replay API")


app.include_router(user.router)
app.include_router(auth.router)
app.include_router(decision.router)
app.include_router(alternative.router)
app.include_router(comment.router)
app.include_router(discussion_thread.router)
app.include_router(decision_version.router)
app.include_router(meeting_notes.router)
app.include_router(rationale.router)
app.include_router(tags.router)
app.include_router(decision.router)


@app.get("/")
def home():
    return {"message": "API is running successfully!"}