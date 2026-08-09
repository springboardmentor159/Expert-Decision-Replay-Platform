from fastapi import FastAPI

from app.routers.user import router as user_router

app = FastAPI(
    title="Expert Decision Replay Platform"
)

app.include_router(user_router)


@app.get("/")
def root():
    return {"message": "API is running"}