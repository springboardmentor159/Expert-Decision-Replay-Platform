from fastapi import FastAPI

from app.core.config import settings
from app.routers.users import router as user_router

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
)

app.include_router(user_router)


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}"
    }