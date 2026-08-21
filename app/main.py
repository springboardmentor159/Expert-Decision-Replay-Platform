from fastapi import FastAPI

from app.routers.users import router as user_router
from app.routers.decisions import router as decision_router
from app.routers import alternatives

app = FastAPI(
    title="Expert Decision Replay Platform"
)

app.include_router(user_router)
app.include_router(decision_router)
app.include_router(alternatives.router)