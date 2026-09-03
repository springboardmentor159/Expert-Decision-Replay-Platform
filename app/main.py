from fastapi import FastAPI

from app.core.config import settings

from app.routers.user import router as user_router

from app.routers.auth import router as auth_router

from app.routers.decision import router as decision_router

from app.routers import alternative

from app.routers import discussion_threads

from app.routers import tag

from app.routers import audit_log

from app.routers import comment

from app.routers import approval

from app.routers import report


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)


app.include_router(user_router)

app.include_router(auth_router)

app.include_router(decision_router)

app.include_router(alternative.router)

app.include_router(discussion_threads.router)

app.include_router(tag.router)

app.include_router(audit_log.router)

app.include_router(comment.router)

app.include_router(approval.router)

app.include_router(report.router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
    }