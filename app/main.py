from fastapi import FastAPI

from app.core.config import settings
from app.routers.users import router as user_router
from app.routers.auth import router as auth_router
from app.routers.decisions import router as decision_router
from app.routers.alternatives import router as alternative_router
from app.routers.comments import router as comment_router
from app.routers.threads import router as thread_router
from app.routers.meeting_notes import router as meeting_note_router


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

# Meeting note
app.include_router(meeting_note_router)

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}"
    }