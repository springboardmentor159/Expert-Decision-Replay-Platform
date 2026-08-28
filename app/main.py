from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import router as auth_router
from app.routers.users import router as user_router
from app.routers.decisions import router as decisions_router
from app.routers.tags import router as tags_router
from app.routers.approvals import router as approvals_router
from app.routers.alternatives import router as alternatives_router
from app.routers.comments import router as comments_router
from app.routers.threads import router as threads_router
from app.routers.meeting_notes import router as meeting_notes_router
from app.routers.dashboard import router as dashboard_router
from app.routers.activities import router as activities_router

app = FastAPI(
    title="Expert Decision Replay Platform",
    description="API for the Expert Decision Replay Platform with Knowledge Repository, Search, Dashboards, and Analytics",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(decisions_router)
app.include_router(tags_router)
app.include_router(approvals_router)
app.include_router(alternatives_router)
app.include_router(comments_router)
app.include_router(threads_router)
app.include_router(meeting_notes_router)
app.include_router(dashboard_router)
app.include_router(activities_router)