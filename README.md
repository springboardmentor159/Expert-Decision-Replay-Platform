# Expert Decision Replay Platform

A FastAPI backend for managing organizational users securely. It supports user registration, predefined roles, professional user profiles, password hashing, JWT login, and protected APIs.

## Features

- Secure password hashing with bcrypt
- JWT-based authentication
- Bearer-token protected user APIs
- Predefined roles:
  - Employee
  - Reviewer
  - Manager
  - Administrator
- User profile fields:
  - Employee ID
  - Department
  - Designation
  - Phone Number
- PostgreSQL database with Alembic migrations
- Swagger API documentation

## Setup

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create `app/.env` with your local values:

```text
APP_NAME=Expert Decision Replay API
DATABASE_URL=your_postgresql_database_url
SECRET_KEY=your_secret_key
```

Do not commit `app/.env` or any secret values.

Apply database migrations:

```powershell
alembic upgrade head
```

Run the application:

```powershell
uvicorn app.main:app --reload
```

Open Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| POST | `/users` | Create a user | No |
| POST | `/users/login` | Login and receive JWT token | No |
| GET | `/users` | Get all users | Bearer token required |
| GET | `/users/{user_id}` | Get one user | Bearer token required |
| PUT | `/users/{user_id}` | Update a user | Bearer token required |
| DELETE | `/users/{user_id}` | Delete a user | Bearer token required |

## Authentication

1. Create a user using `POST /users`.
2. Log in through `POST /users/login`.
3. Copy the returned `access_token`.
4. In Swagger, click **Authorize** and paste the token.
5. Access protected user endpoints.

Requests without a valid token return `401 Unauthorized`.

## Role Validation

Only these roles are accepted:

```text
Employee
Reviewer
Manager
Administrator
```

Any other role is rejected automatically.

## Testing Completed

- User creation returns `201 Created`
- Invalid roles return `422 Unprocessable Entity`
- Login returns a JWT access token
- Protected APIs reject missing tokens with `401 Unauthorized`
- Protected APIs work with a valid Bearer token
- Profile fields are stored in PostgreSQL
