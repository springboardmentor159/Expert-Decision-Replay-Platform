# Expert Decision Replay Platform

FastAPI backend and browser frontend for capturing decisions, comparing alternatives, collaborating in discussions, completing approvals, and reporting on decision history.

## Run locally

1. Create and activate the virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Start the application with `python -m uvicorn main:app --reload`.
4. Open `http://127.0.0.1:8000/` for the frontend or `/docs` for the API documentation.

The frontend is served by FastAPI from `frontend/` and uses the same origin, so no separate frontend build step is required. It stores the JWT in session storage, handles expired sessions and permission errors, and resolves the logged-in user's role through the authenticated users endpoint.

## Included workflows

- Registration and JWT login/logout
- Role-aware dashboards and navigation
- Decision creation, editing, filtering, status transitions, and soft deletion
- Alternative analysis and comparison
- Decision comments, approvals, timelines, and version history
- Knowledge repository search
- Decision reports with PDF and Excel downloads
- Administrator audit activity

## Configuration

Copy `.env.example` to `.env` and provide deployment-specific values. Never commit `.env`, credentials, tokens, or database passwords.

## API authentication
1. Use the frontend registration form or `POST /users` to create a new user.
   - Submit JSON with `full_name`, `email`, `role`, `employee_id`, `department`, `designation`, `phone_number`, and `password`.
2. Use the frontend login form or `POST /token` to log in.
   - In Swagger, click `Try it out`.
   - Submit `username` as the user email and `password`.
   - Copy the returned `access_token`.
3. For direct API work, click `Authorize` in the top-right of Swagger.
   - Enter `Bearer <access_token>` (for example `Bearer ey...`).
   - Click `Authorize` and then `Close`.
4. Call the protected `GET /users` endpoint.
   - It should return a list of users only when the token is valid.
5. If you omit or use an invalid token, Swagger returns `401 Unauthorized`.

