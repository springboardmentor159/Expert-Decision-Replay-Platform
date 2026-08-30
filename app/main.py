from fastapi import FastAPI

from app.db.base import Base
from app.db.database import engine

# Import all models so SQLAlchemy knows about them
import app.models
from fastapi import FastAPI
from app.routers.meeting_notes import router as meeting_note_router
from app.routers.auth import router as auth_router
from app.routers.users import router as user_router
from app.routers.decisions import router as decision_router
from app.routers.alternatives import router as alternative_router
from app.routers.comments import router as comment_router
from app.routers.discussion_threads import router as discussion_thread_router
from app.routers import tags
from app.routers.scoring import router as scoring_router
from app.routers.expert_evaluations import router as expert_evaluation_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Expert Decision Replay Platform"
)


app.include_router(user_router)

app.include_router(auth_router)

app.include_router(decision_router)

app.include_router(alternative_router)

app.include_router(comment_router)

app.include_router(discussion_thread_router)

app.include_router(meeting_note_router)

app.include_router(tags.router)

app.include_router(scoring_router)

app.include_router(expert_evaluation_router)