from fastapi import FastAPI
from app.routers import user

app = FastAPI(title="Expert Decision Replay API")

app.include_router(user.router)

@app.get("/")
def home():
    return {"message": "API is running"}