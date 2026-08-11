from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.routers.users import router as user_router
from app.routers.auth import router as auth_router
from app.routers.test_endpoints import router as test_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "Expert Decision Replay Platform API. "
        "Use **POST /auth/token** to obtain a JWT, then click **Authorize 🔒** "
        "and paste the token as: `Bearer <your-token>`"
    ),
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(test_router)


# ── Inject OAuth2 Bearer security scheme into OpenAPI so Swagger shows 🔒 ──
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add Bearer token security scheme
    schema.setdefault("components", {})
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # Apply it globally to all operations
    for path_item in schema.get("paths", {}).values():
        for operation in path_item.values():
            if isinstance(operation, dict):
                operation.setdefault("security", [{"BearerAuth": []}])

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi