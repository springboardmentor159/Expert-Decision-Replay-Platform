# Discussion and Collaboration Module - API Reference

## Quick Reference Guide

### Base URL
```
http://127.0.0.1:8000
```

### Authentication
All endpoints (except /token and /users POST) require JWT Bearer token:
```
Authorization: Bearer <access_token>
```

---

## Comments API

### Create Comment
```
POST /decisions/{decision_id}/comments
Content-Type: application/json

{
  "content": "Comment text here"
}
```
**Response**: 201 Created  
**Error**: 404 Decision not found, 401 Unauthorized

---

### Get All Comments for Decision
```
GET /decisions/{decision_id}/comments
```
**Response**: 200 OK (array of comments, excluding thread comments)  
**Error**: 404 Decision not found, 401 Unauthorized

---

### Get Specific Comment
```
GET /comments/{comment_id}
```
**Response**: 200 OK  
**Error**: 404 Comment not found, 401 Unauthorized

---

### Update Comment
```
PUT /comments/{comment_id}
Content-Type: application/json

{
  "content": "Updated comment text"
}
```
**Response**: 200 OK  
**Error**: 403 Forbidden (not owner), 404 Not found, 401 Unauthorized

---

### Delete Comment
```
DELETE /comments/{comment_id}
```
**Response**: 204 No Content  
**Error**: 403 Forbidden (not owner), 404 Not found, 401 Unauthorized

---

## Discussion Threads API

### Create Thread
```
POST /decisions/{decision_id}/threads
Content-Type: application/json

{
  "title": "Thread title",
  "description": "Thread description"
}
```
**Response**: 201 Created  
**Error**: 404 Decision not found, 401 Unauthorized

---

### Get All Threads for Decision
```
GET /decisions/{decision_id}/threads
```
**Response**: 200 OK (array of threads)  
**Error**: 404 Decision not found, 401 Unauthorized

---

### Get Specific Thread
```
GET /threads/{thread_id}
```
**Response**: 200 OK  
**Error**: 404 Thread not found, 401 Unauthorized

---

### Update Thread
```
PUT /threads/{thread_id}
Content-Type: application/json

{
  "title": "Updated title",
  "description": "Updated description",
  "status": "Open|Resolved|Closed"
}
```
Note: All fields are optional. Include only fields you want to update.

**Response**: 200 OK  
**Error**: 403 Forbidden (not creator), 404 Not found, 401 Unauthorized

---

### Delete Thread
```
DELETE /threads/{thread_id}
```
**Response**: 204 No Content  
**Error**: 403 Forbidden (not creator), 404 Not found, 401 Unauthorized

---

### Add Reply to Thread
```
POST /threads/{thread_id}/comments
Content-Type: application/json

{
  "content": "Reply text"
}
```
**Response**: 201 Created  
**Error**: 404 Thread not found, 401 Unauthorized

---

### Get All Replies to Thread
```
GET /threads/{thread_id}/comments
```
**Response**: 200 OK (array of comment replies)  
**Error**: 404 Thread not found, 401 Unauthorized

---

## Meeting Notes API

### Create Meeting Note
```
POST /decisions/{decision_id}/meeting-notes
Content-Type: application/json

{
  "title": "Meeting title",
  "content": "Meeting notes content",
  "meeting_date": "2025-01-15T14:00:00"
}
```
**Response**: 201 Created  
**Error**: 404 Decision not found, 401 Unauthorized

---

### Get All Meeting Notes for Decision
```
GET /decisions/{decision_id}/meeting-notes
```
**Response**: 200 OK (array of meeting notes)  
**Error**: 404 Decision not found, 401 Unauthorized

---

### Get Specific Meeting Note
```
GET /meeting-notes/{note_id}
```
**Response**: 200 OK  
**Error**: 404 Meeting note not found, 401 Unauthorized

---

### Update Meeting Note
```
PUT /meeting-notes/{note_id}
Content-Type: application/json

{
  "title": "Updated title",
  "content": "Updated content",
  "meeting_date": "2025-01-15T15:00:00"
}
```
Note: All fields are optional.

**Response**: 200 OK  
**Error**: 403 Forbidden (not creator), 404 Not found, 401 Unauthorized

---

### Delete Meeting Note
```
DELETE /meeting-notes/{note_id}
```
**Response**: 204 No Content  
**Error**: 403 Forbidden (not creator), 404 Not found, 401 Unauthorized

---

## Decision Rationale API

### Update Decision Rationale
```
PUT /decisions/{decision_id}/rationale
Content-Type: application/json

{
  "rationale": "Explanation of why this decision was made"
}
```
**Response**: 200 OK (returns full decision object)  
**Error**: 404 Decision not found, 401 Unauthorized

---

## Authentication API

### Login
```
POST /token
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=password123
```
**Response**: 200 OK
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```
**Error**: 401 Unauthorized (invalid credentials)

---

## Response Format

### Success Responses

#### Comment Response
```json
{
  "id": 1,
  "decision_id": 1,
  "user_id": 1,
  "thread_id": null,
  "content": "Comment text",
  "created_at": "2025-01-15T10:05:00+00:00",
  "updated_at": "2025-01-15T10:05:00+00:00"
}
```

#### DiscussionThread Response
```json
{
  "id": 1,
  "decision_id": 1,
  "created_by": 1,
  "title": "Thread title",
  "description": "Thread description",
  "status": "Open",
  "created_at": "2025-01-15T10:10:00+00:00",
  "updated_at": "2025-01-15T10:10:00+00:00"
}
```

#### MeetingNote Response
```json
{
  "id": 1,
  "decision_id": 1,
  "created_by": 1,
  "title": "Meeting title",
  "content": "Meeting notes",
  "meeting_date": "2025-01-15T14:00:00",
  "created_at": "2025-01-15T14:05:00+00:00",
  "updated_at": "2025-01-15T14:05:00+00:00"
}
```

### Error Responses

#### 404 Not Found
```json
{
  "detail": "Decision not found"
}
```

#### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

#### 403 Forbidden
```json
{
  "detail": "You do not have permission to modify this resource"
}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "content"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Status Codes Reference

| Code | Meaning |
|------|---------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created successfully |
| 204 | No Content - Request succeeded, no content to return |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing or invalid JWT |
| 403 | Forbidden - User lacks permission |
| 404 | Not Found - Resource doesn't exist |
| 422 | Unprocessable Entity - Validation failed |
| 500 | Internal Server Error |

---

## Authorization Rules

### Comments
- **Create**: Authenticated user (JWT required)
- **Read**: Authenticated user
- **Update**: Comment author OR admin/manager role
- **Delete**: Comment author OR admin/manager role

### Discussion Threads
- **Create**: Authenticated user
- **Read**: Authenticated user
- **Update**: Thread creator OR admin/manager role
- **Delete**: Thread creator OR admin/manager role

### Meeting Notes
- **Create**: Authenticated user
- **Read**: Authenticated user
- **Update**: Note creator OR admin/manager role
- **Delete**: Note creator OR admin/manager role

### Decision Rationale
- **Update**: Authenticated user (any authenticated user can update)

---

## Field Constraints

### Comment
- `content`: Required, string (1+ characters)

### DiscussionThread
- `title`: Required, string (1+ characters)
- `description`: Required, string (1+ characters)
- `status`: Optional, must be one of: "Open", "Resolved", "Closed"

### MeetingNote
- `title`: Required, string (1+ characters)
- `content`: Required, string (1+ characters)
- `meeting_date`: Required, ISO 8601 datetime string

### Decision Rationale
- `rationale`: Required, string (1+ characters)
