from fastapi import FastAPI

from app.routers import user, decision, alternative, auth

app = FastAPI(title="Expert Decision Replay API")

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(decision.router)
app.include_router(alternative.router)


@app.get("/")
def home():
    return {"message": "API is running successfully!"}