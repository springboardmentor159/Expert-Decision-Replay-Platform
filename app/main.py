from fastapi import FastAPI

from app.core.config import settings
from app.routers.user import router as user_router


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)


app.include_router(user_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
    }