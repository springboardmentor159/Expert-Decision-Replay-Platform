from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routers.users import router as user_router
from app.routers.auth import router as auth_router
from app.routers.decisions import router as decision_router
from app.routers import alternative
from app.routers import comment
from app.routers import discussion_thread
from app.routers import meeting_note
from app.routers import rationale
from app.routers import tag
from app.routers import dashboard, activity, approval
from app.routers import audit
from app.routers import reports
from app.routers import document

app = FastAPI(
    title="Expert Decision Replay Platform"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(decision_router)
app.include_router(alternative.router)
app.include_router(comment.router)
app.include_router(discussion_thread.router)
app.include_router(meeting_note.router)
app.include_router(rationale.router)
app.include_router(tag.router)
app.include_router(dashboard.router)
app.include_router(activity.router)
app.include_router(approval.router)
app.include_router(audit.router)
app.include_router(reports.router)
app.include_router(document.router)