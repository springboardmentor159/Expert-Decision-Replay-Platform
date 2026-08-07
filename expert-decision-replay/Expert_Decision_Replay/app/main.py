from fastapi import FastAPI
from app.database import engine, Base
import app.models.user as models  # <--- MUST import models before create_all!

# Create tables in PostgreSQL
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expert Decision Replay Platform")

# Include your router
from app.routers import users
app.include_router(users.router)