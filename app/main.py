from fastapi import FastAPI
from fastapi.security import HTTPBearer

from app.core.config import settings
from app.routers.user import router as user_router
from app.routers.auth import router as auth_router
from app.routers.decision import router as decision_router

app = FastAPI(
    title=settings.app_name,
    version="1.0.0"
)

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(decision_router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name
    }