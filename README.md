# Backend User Management

## Description
This project is a backend application for user management. It provides APIs to create, read, update, and delete user information.

## Features
- User Registration
- User Login
- Get User Details
- Update User Information
- Delete User

## Technologies Used
- Java
- Spring Boot
- Maven
- MySQL
- REST API

## How to Run
1. Clone the repository.
2. Open the project in your IDE.
3. Create and activate a Python virtual environment.
4. Install dependencies with `pip install fastapi uvicorn python-jose[cryptography] bcrypt python-multipart`.
5. Run the app with `python -m uvicorn main:app --reload`.
6. Open Swagger at `http://127.0.0.1:8000/docs`.

## Swagger Token Authentication Walkthrough
1. Use the `POST /users` endpoint to create a new user.
   - Submit JSON with `full_name`, `email`, `role`, `employee_id`, `department`, `designation`, `phone_number`, and `password`.
2. Use `POST /token` to log in.
   - In Swagger, click `Try it out`.
   - Submit `username` as the user email and `password`.
   - Copy the returned `access_token`.
3. Click `Authorize` in the top-right of Swagger.
   - Enter `Bearer <access_token>` (for example `Bearer ey...`).
   - Click `Authorize` and then `Close`.
4. Call the protected `GET /users` endpoint.
   - It should return a list of users only when the token is valid.
5. If you omit or use an invalid token, Swagger returns `401 Unauthorized`.

## Author
Ramya
