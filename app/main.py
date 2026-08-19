from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import router as auth_router
from app.routers.users import router as user_router
from app.routers.decisions import router as decisions_router
from app.routers.alternatives import router as alternatives_router

app = FastAPI(
    title="Expert Decision Replay Platform",
    description="API for the Expert Decision Replay Platform with User Management and JWT Authentication",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(decisions_router)
app.include_router(alternatives_router)