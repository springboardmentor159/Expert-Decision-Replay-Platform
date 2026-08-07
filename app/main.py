# from fastapi import FastAPI

# from app.core.config import settings


# app = FastAPI(
#     title=settings.app_name,
#     version="1.0.0"
# )


# @app.get("/health")
# def health_check():
#     return {
#         "status": "ok",
#         "service": settings.app_name
#     }


from fastapi import FastAPI

from app.routers.users import router as user_router

app = FastAPI(
    title="Expert Decision Replay Platform"
)

app.include_router(user_router)