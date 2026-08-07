from fastapi import FastAPI

from db.database import engine
from db.base import Base

import app.models.user

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expert Decision Replay Platform")

from app.routers import users
app.include_router(users.router)