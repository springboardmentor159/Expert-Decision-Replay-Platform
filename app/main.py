from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.users import router as user_router
from app.routers.decisions import router as decision_router
from app.routers.alternatives import router as alternative_router
app = FastAPI(
    title="Expert Decision Replay Platform"
)

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(decision_router)
app.include_router(alternative_router)