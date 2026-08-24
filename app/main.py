from fastapi import FastAPI

from app.routers.users import router as user_router
from app.routers.decisions import router as decision_router
from app.routers import alternatives
from app.routers import comments
from app.routers import threads
from app.routers import meeting_notes


app = FastAPI(
    title="Expert Decision Replay Platform"
)


app.include_router(user_router)

app.include_router(decision_router)

app.include_router(alternatives.router)

app.include_router(comments.router)

app.include_router(threads.router)

app.include_router(meeting_notes.router)