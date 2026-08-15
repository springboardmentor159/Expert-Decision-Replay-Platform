from fastapi import FastAPI

from app.routers import user, decision

app = FastAPI(title="Expert Decision Replay API")


app.include_router(user.router)
app.include_router(decision.router)


@app.get("/")
def home():
    return {"message": "API is running successfully!"}