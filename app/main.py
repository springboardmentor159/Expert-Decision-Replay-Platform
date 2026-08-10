from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.routers.user import router as user_router

app = FastAPI(
    title="Expert Decision Replay Platform"
)

app.include_router(user_router)
app.include_router(auth_router)


@app.get("/")
def root():
    return {"message": "API is running"}