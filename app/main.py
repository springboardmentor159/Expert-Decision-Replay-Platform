from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.routers.users import router as user_router
from app.routers.auth import router as auth_router
from app.routers.test_endpoints import router as test_router
from app.core.config import settings

DESCRIPTION = """
## Expert Decision Replay Platform — API

### ⚠️ How to log in via Swagger

**Step 1 — Register a user first**
> `POST /users` → fill in full_name, email, password, role, etc. → Execute

**Step 2 — Click Authorize 🔒 (top right)**
> - **Username**: enter the **email** you registered (e.g. `rahul@gmail.com`)
> - **Password**: enter your password
> - Leave Client ID and Client Secret blank
> - Click **Authorize** → then **Close**

**Step 3 — Call protected endpoints**
> All 🔒 padlock endpoints now work automatically.

---

### Roles (only these are accepted)
| Role | Description |
|------|-------------|
| `Employee` | Standard staff |
| `Reviewer` | Reviews decisions |
| `Manager` | Manages teams |
| `Administrator` | Full access |

### Departments (only these are accepted)
`IT` · `CAC`

### Status codes
| Code | Meaning |
|------|---------|
| 401 | Missing or invalid token |
| 403 | Authenticated but wrong role/department |
| 409 | Duplicate email or employee ID |
"""

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=DESCRIPTION,
    # Control tag order so Users (Register) appears before Auth
    openapi_tags=[
        {"name": "Users",               "description": "Register and manage users"},
        {"name": "Authentication",      "description": "Login and obtain JWT tokens"},
        {"name": "Authorization Tests", "description": "Test role and department access"},
    ],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(test_router)


# ── OAuth2 Password flow — Swagger shows Username + Password form ─────────────
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
    )

    # OAuth2 Password flow: Swagger shows Username + Password form,
    # POSTs to /auth/token, stores the JWT automatically.
    schema.setdefault("components", {})
    schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/auth/token",
                    "scopes": {}
                }
            },
            "description": "Enter your **email** as Username and your **password**."
        }
    }

    # Public endpoints that do NOT require a token
    public = {
        ("/users", "post"),       # Register — no token needed
        ("/auth/token", "post"),  # OAuth2 login form
        ("/auth/login", "post"),  # JSON login
    }

    for path, path_item in schema.get("paths", {}).items():
        for method, operation in path_item.items():
            if not isinstance(operation, dict):
                continue
            if (path, method) not in public:
                operation.setdefault(
                    "security", [{"OAuth2PasswordBearer": []}]
                )

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi