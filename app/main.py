from fastapi import FastAPI

from app.routers import (
    users,
    login,
    decisions,
    alternatives,
    comments,
    tags
)

app = FastAPI(
    title="Expert Decision Replay Platform",
    description="API for managing decisions, alternatives, comments and tags",
    version="1.0.0"
)


app.include_router(users.router)
app.include_router(login.router)
app.include_router(decisions.router)
app.include_router(alternatives.router)
app.include_router(comments.router)
app.include_router(tags.router)


@app.get("/")
def root():
    return {
        "message": "Expert Decision Replay Platform API is running"
    }