from fastapi import FastAPI

from app.routers.users import router as user_router
from app.routers.auth import router as auth_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="1.0.0"
)


app.include_router(auth_router)
app.include_router(user_router)