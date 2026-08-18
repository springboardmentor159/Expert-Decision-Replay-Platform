from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.routers.alternative import alternatives_router, router as alternative_router
from app.routers.decision import router as decision_router
from app.routers.user import router as user_router

app = FastAPI(
    title="Expert Decision Replay Platform"
)

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(decision_router)
app.include_router(alternative_router)
app.include_router(alternatives_router)


@app.get("/")
def root():
    return {"message": "API is running"}