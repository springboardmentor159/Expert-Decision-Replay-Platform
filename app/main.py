from fastapi import FastAPI

from app.routers.users import router as user_router
from app.routers.auth import router as auth_router
from app.routers.decisions import router as decision_router
from app.routers import alternative
from app.routers import comment
from app.routers import discussion_thread
from app.routers import meeting_note
from app.routers import rationale

app = FastAPI(
    title="Expert Decision Replay Platform"
)

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(decision_router)
app.include_router(alternative.router)
app.include_router(comment.router)
app.include_router(discussion_thread.router)
app.include_router(meeting_note.router)
app.include_router(rationale.router)