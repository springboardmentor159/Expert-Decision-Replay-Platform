from fastapi import FastAPI

from app.routers.users import router as user_router
from app.routers.auth import router as auth_router


app = FastAPI(
    title="Expert Decision Replay Platform"
)

app.include_router(user_router)
app.include_router(auth_router)