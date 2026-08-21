from fastapi import FastAPI

from app.database import engine, Base

# Import models so SQLAlchemy knows about all tables
import app.models.user
import app.models.decision
import app.models.alternative


# Create tables in PostgreSQL
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Expert Decision Replay Platform"
)


# Include routers
from app.routers import users, login, decisions, alternatives


app.include_router(users.router)
app.include_router(login.router)
app.include_router(decisions.router)
app.include_router(alternatives.router)