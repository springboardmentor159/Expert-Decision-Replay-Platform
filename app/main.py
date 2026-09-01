from fastapi import FastAPI

from app.routers.users import router as user_router
from app.routers.auth import router as auth_router
from app.routers.decisions import router as decisions_router
from app.routers.alternatives import router as alternatives_router
from app.routers import comment
from app.routers import discussion_thread
from app.routers.tags import router as tags_router

app = FastAPI(
    title="Expert Decision Replay Platform"
)


app.include_router(user_router)
app.include_router(auth_router)
app.include_router(decisions_router)
app.include_router(alternatives_router)
app.include_router(comment.router)
app.include_router(discussion_thread.router)
app.include_router(tags_router)