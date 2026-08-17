# Decision Management API - Quick Reference Guide

## 🚀 Base URL
```
http://localhost:8000
```

## 🔐 Authentication
All endpoints (except `/token` and `/health`) require JWT authentication.

### Get JWT Token
```http
POST /token
Content-Type: application/x-www-form-urlencoded

username={email}&password={password}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Using Token in Requests
```http
Authorization: Bearer {access_token}
```

---

## 📋 Decision Endpoints

### 1. Create Decision
```http
POST /decisions
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "string",
  "problem_statement": "string",
  "category": "string"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "title": "string",
  "problem_statement": "string",
  "category": "string",
  "status": "Draft",
  "created_by": 1,
  "created_at": "2026-08-17T16:56:36.496287+05:30",
  "updated_at": "2026-08-17T16:56:36.496287+05:30"
}
```

---

### 2. Get All Decisions
```http
GET /decisions
Authorization: Bearer {token}
```

**Optional Query Parameters:**
- `status` - Filter by status (Draft, Under Review, Approved, Rejected, Archived)
- `category` - Filter by category

**Examples:**
```
GET /decisions
GET /decisions?status=Draft
GET /decisions?category=Technology
GET /decisions?status=Approved&category=Technology
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "title": "string",
    "problem_statement": "string",
    "category": "string",
    "status": "Draft",
    "created_by": 1,
    "created_at": "2026-08-17T16:56:36.496287+05:30",
    "updated_at": "2026-08-17T16:56:36.496287+05:30"
  }
]
```

---

### 3. Get Specific Decision
```http
GET /decisions/{decision_id}
Authorization: Bearer {token}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "string",
  "problem_statement": "string",
  "category": "string",
  "status": "Draft",
  "created_by": 1,
  "created_at": "2026-08-17T16:56:36.496287+05:30",
  "updated_at": "2026-08-17T16:56:36.496287+05:30"
}
```

**Errors:**
- `404 Not Found` - Decision does not exist

---

### 4. Update Decision
```http
PUT /decisions/{decision_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "string (optional)",
  "problem_statement": "string (optional)",
  "category": "string (optional)"
}
```

**Immutable Fields (Cannot be changed):**
- `id` - Primary key
- `created_by` - User who created the decision
- `created_at` - Creation timestamp

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Updated Title",
  "problem_statement": "Updated description",
  "category": "Technology",
  "status": "Draft",
  "created_by": 1,
  "created_at": "2026-08-17T16:56:36.496287+05:30",
  "updated_at": "2026-08-17T16:57:00.123456+05:30"
}
```

**Errors:**
- `404 Not Found` - Decision does not exist
- `422 Unprocessable Entity` - Invalid request data

---

### 5. Update Decision Status
```http
PATCH /decisions/{decision_id}/status
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "Draft | Under Review | Approved | Rejected | Archived"
}
```

**Valid Status Values:**
- `Draft` - Initial status
- `Under Review` - Being reviewed
- `Approved` - Approved
- `Rejected` - Rejected
- `Archived` - Archived/Completed

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "string",
  "problem_statement": "string",
  "category": "string",
  "status": "Under Review",
  "created_by": 1,
  "created_at": "2026-08-17T16:56:36.496287+05:30",
  "updated_at": "2026-08-17T16:57:00.123456+05:30"
}
```

**Errors:**
- `404 Not Found` - Decision does not exist
- `422 Unprocessable Entity` - Invalid status value
  ```json
  {
    "detail": [
      {
        "type": "enum",
        "loc": ["body", "status"],
        "msg": "Input should be 'Draft', 'Under Review', 'Approved', 'Rejected' or 'Archived'",
        "input": "Completed",
        "ctx": {
          "expected": "'Draft', 'Under Review', 'Approved', 'Rejected' or 'Archived'"
        }
      }
    ]
  }
  ```

---

### 6. Delete Decision
```http
DELETE /decisions/{decision_id}
Authorization: Bearer {token}
```

**Response:** `204 No Content` (empty body)

**Note:** Soft delete - sets status to "Archived"

**Errors:**
- `404 Not Found` - Decision does not exist

---

## 📊 Filter Examples

### Filter by Status
```http
GET /decisions?status=Draft
GET /decisions?status=Under%20Review
GET /decisions?status=Approved
GET /decisions?status=Rejected
GET /decisions?status=Archived
```

### Filter by Category
```http
GET /decisions?category=Technology
GET /decisions?category=Infrastructure
GET /decisions?category=Process
```

### Combined Filters
```http
GET /decisions?status=Approved&category=Technology
GET /decisions?status=Under%20Review&category=Infrastructure
```

---

## 🔍 Error Responses

### 401 Unauthorized
**When:** Missing or invalid JWT token
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
**When:** Decision does not exist
```json
{
  "detail": "Decision not found"
}
```

### 422 Unprocessable Entity
**When:** Invalid request data (e.g., invalid status)
```json
{
  "detail": [
    {
      "type": "enum",
      "loc": ["body", "status"],
      "msg": "Input should be 'Draft', 'Under Review', 'Approved', 'Rejected' or 'Archived'",
      "input": "InvalidStatus"
    }
  ]
}
```

### 400 Bad Request
**When:** Invalid request format
```json
{
  "detail": "string describing the error"
}
```

---

## 📝 HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created successfully |
| 204 | No Content - Successful delete |
| 400 | Bad Request - Invalid request format |
| 401 | Unauthorized - Missing or invalid token |
| 404 | Not Found - Resource does not exist |
| 422 | Unprocessable Entity - Invalid data (validation error) |
| 500 | Internal Server Error - Server error |

---

## 🧪 cURL Examples

### Login
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password123"
```

### Create Decision
```bash
curl -X POST "http://localhost:8000/decisions" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Migrate to PostgreSQL",
    "problem_statement": "Current system uses SQLite",
    "category": "Technology"
  }'
```

### Get All Draft Decisions
```bash
curl -X GET "http://localhost:8000/decisions?status=Draft" \
  -H "Authorization: Bearer {token}"
```

### Update Decision
```bash
curl -X PUT "http://localhost:8000/decisions/1" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "problem_statement": "Updated description",
    "category": "Infrastructure"
  }'
```

### Update Status
```bash
curl -X PATCH "http://localhost:8000/decisions/1/status" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Under Review"
  }'
```

### Delete Decision
```bash
curl -X DELETE "http://localhost:8000/decisions/1" \
  -H "Authorization: Bearer {token}"
```

---

## 🎯 Testing in Swagger

Access Swagger UI at:
```
http://localhost:8000/docs
```

Features:
- Try out all endpoints
- See request/response schemas
- Test with different parameters
- Validate authentication

---

## 💡 Tips & Best Practices

1. **Always include Authorization header** for protected endpoints
2. **Status values are case-sensitive** (use exact casing)
3. **Fields to always provide:** title, problem_statement, category
4. **Use query parameters for filtering** - don't retrieve all decisions
5. **Check timestamps** - created_at won't change, updated_at will
6. **Handle 404 errors** - decision might be deleted or archived
7. **Validate token expiration** - get new token if 401 occurs
8. **Use combined filters** for better performance on large datasets

---

## 📚 Related Endpoints

- **User Management:** See User API documentation
- **Authentication:** POST /token endpoint
- **Health Check:** GET /health endpoint

---

**Last Updated:** 2026-08-17
**API Version:** 1.0.0
