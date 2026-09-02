# Discussion and Collaboration Module - Swagger Testing Guide

## Overview
This guide walks through testing the complete Discussion and Collaboration Module API through Swagger UI.

Access Swagger: http://127.0.0.1:8000/docs

---

## Step 1: Login and Obtain JWT Token

### Endpoint: POST /token

**Description**: Authenticate a user and receive a JWT token required for all subsequent API calls.

**Request Body:**
```
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Expected Response (200):**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

**Copy the `access_token` value** - you'll need it for all subsequent API calls.

**In Swagger:**
1. Click "POST /token"
2. Click "Try it out"
3. Enter email as username and password
4. Click "Execute"
5. Copy the access_token from the response

---

## Step 2: Authorize Swagger with JWT

**In Swagger:**
1. Click the green "Authorize" button at the top
2. Enter: `Bearer <your_access_token>`
3. Click "Authorize"
4. Click "Close"

Now all API requests will include your JWT token.

---

## Step 3: Create or Select a Decision

### Endpoint: POST /decisions

**Description**: Create a new decision to add comments to.

**Request Body:**
```json
{
  "title": "Select Database for New Project",
  "problem_statement": "We need to choose a database for our new microservices architecture. Options include PostgreSQL, MongoDB, and Cassandra.",
  "category": "Technology"
}
```

**Expected Response (201):**
```json
{
  "id": 1,
  "title": "Select Database for New Project",
  "problem_statement": "We need to choose a database...",
  "category": "Technology",
  "status": "Draft",
  "rationale": null,
  "created_by": 1,
  "created_at": "2025-01-15T10:00:00+00:00",
  "updated_at": "2025-01-15T10:00:00+00:00"
}
```

**Note the `decision_id` (e.g., 1)** - you'll use it in subsequent requests.

---

## Step 4: Create Comments (3 minimum)

### Endpoint: POST /decisions/{decision_id}/comments

**Description**: Add a comment to the decision.

#### Comment 1:
```json
{
  "content": "PostgreSQL provides strong relational support and has mature tooling for microservices architectures."
}
```

#### Comment 2:
```json
{
  "content": "MongoDB might be better for flexible schema requirements and horizontal scaling."
}
```

#### Comment 3:
```json
{
  "content": "We should consider operational costs and team expertise. PostgreSQL has larger ecosystem and community support."
}
```

**Expected Response (201 for each):**
```json
{
  "id": 1,
  "decision_id": 1,
  "user_id": 1,
  "thread_id": null,
  "content": "PostgreSQL provides...",
  "created_at": "2025-01-15T10:05:00+00:00",
  "updated_at": "2025-01-15T10:05:00+00:00"
}
```

**Note the comment IDs** for later use (e.g., 1, 2, 3).

---

## Step 5: Retrieve All Comments for Decision

### Endpoint: GET /decisions/{decision_id}/comments

**Description**: Get all comments for a specific decision.

**Expected Response (200):**
```json
[
  {
    "id": 1,
    "decision_id": 1,
    "user_id": 1,
    "thread_id": null,
    "content": "PostgreSQL provides...",
    "created_at": "2025-01-15T10:05:00+00:00",
    "updated_at": "2025-01-15T10:05:00+00:00"
  },
  {
    "id": 2,
    "decision_id": 1,
    "user_id": 1,
    "thread_id": null,
    "content": "MongoDB might be...",
    "created_at": "2025-01-15T10:06:00+00:00",
    "updated_at": "2025-01-15T10:06:00+00:00"
  },
  ...
]
```

---

## Step 6: Retrieve One Comment by ID

### Endpoint: GET /comments/{comment_id}

**Description**: Get a specific comment by ID.

**Expected Response (200):**
```json
{
  "id": 1,
  "decision_id": 1,
  "user_id": 1,
  "thread_id": null,
  "content": "PostgreSQL provides...",
  "created_at": "2025-01-15T10:05:00+00:00",
  "updated_at": "2025-01-15T10:05:00+00:00"
}
```

**If comment doesn't exist (404):**
```json
{
  "detail": "Comment not found"
}
```

---

## Step 7: Update a Comment

### Endpoint: PUT /comments/{comment_id}

**Description**: Update the content of a comment (only author or admin can do this).

**Request Body:**
```json
{
  "content": "PostgreSQL appears to be the most suitable option because our application requires strong relational support and we have team expertise with SQL databases."
}
```

**Expected Response (200):**
```json
{
  "id": 1,
  "decision_id": 1,
  "user_id": 1,
  "thread_id": null,
  "content": "PostgreSQL appears to be...",
  "created_at": "2025-01-15T10:05:00+00:00",
  "updated_at": "2025-01-15T10:07:00+00:00"  // Updated timestamp
}
```

---

## Step 8: Create a Discussion Thread

### Endpoint: POST /decisions/{decision_id}/threads

**Description**: Create a discussion thread for more structured conversations.

**Request Body:**
```json
{
  "title": "Database Scalability",
  "description": "Let's discuss the scalability requirements before finalizing the database choice. We need to consider current and future data volume."
}
```

**Expected Response (201):**
```json
{
  "id": 1,
  "decision_id": 1,
  "created_by": 1,
  "title": "Database Scalability",
  "description": "Let's discuss...",
  "status": "Open",
  "created_at": "2025-01-15T10:10:00+00:00",
  "updated_at": "2025-01-15T10:10:00+00:00"
}
```

**Note the thread ID** (e.g., 1) for next step.

---

## Step 9: Add Replies to Thread

### Endpoint: POST /threads/{thread_id}/comments

**Description**: Add replies to a discussion thread.

#### Reply 1:
```json
{
  "content": "PostgreSQL can handle millions of rows efficiently with proper indexing and partitioning strategies."
}
```

#### Reply 2:
```json
{
  "content": "We should also test with our actual data volumes before making a final decision."
}
```

**Expected Response (201 for each):**
```json
{
  "id": 4,
  "decision_id": 1,
  "user_id": 1,
  "thread_id": 1,
  "content": "PostgreSQL can handle...",
  "created_at": "2025-01-15T10:12:00+00:00",
  "updated_at": "2025-01-15T10:12:00+00:00"
}
```

---

## Step 10: Create Meeting Notes

### Endpoint: POST /decisions/{decision_id}/meeting-notes

**Description**: Record meeting notes about the decision.

**Request Body:**
```json
{
  "title": "Database Selection Meeting - January 15",
  "content": "Team discussed three database options. Consensus was that PostgreSQL meets our current requirements best. MongoDB's flexibility was noted but concerns about operational complexity led team to prefer PostgreSQL.",
  "meeting_date": "2025-01-15T14:00:00"
}
```

**Expected Response (201):**
```json
{
  "id": 1,
  "decision_id": 1,
  "created_by": 1,
  "title": "Database Selection Meeting...",
  "content": "Team discussed...",
  "meeting_date": "2025-01-15T14:00:00",
  "created_at": "2025-01-15T14:05:00+00:00",
  "updated_at": "2025-01-15T14:05:00+00:00"
}
```

---

## Step 11: Add Decision Rationale

### Endpoint: PUT /decisions/{decision_id}/rationale

**Description**: Record the rationale explaining why this decision was made.

**Request Body:**
```json
{
  "rationale": "PostgreSQL was selected because it provided the best balance between reliability, feasibility, cost, and operational risk. The team has extensive experience with SQL databases, and PostgreSQL's ACID compliance ensures data integrity for our microservices architecture."
}
```

**Expected Response (200):**
```json
{
  "id": 1,
  "title": "Select Database for New Project",
  "problem_statement": "We need to choose...",
  "category": "Technology",
  "status": "Draft",
  "rationale": "PostgreSQL was selected because...",
  "created_by": 1,
  "created_at": "2025-01-15T10:00:00+00:00",
  "updated_at": "2025-01-15T14:10:00+00:00"
}
```

---

## Step 12: Test Authentication (401 Unauthorized)

### Without JWT Token

Remove the Authorization header or don't authorize in Swagger:

1. Click the Authorize button and logout (or don't set the header)
2. Try to call any endpoint, e.g., `GET /decisions/{decision_id}/comments`

**Expected Response (401):**
```json
{
  "detail": "Could not validate credentials"
}
```

---

## Step 13: Test Authorization (403 Forbidden)

### Attempting to modify another user's comment

To test this, you would need:
1. Two different user accounts with JWT tokens
2. User A creates a comment
3. User B tries to update or delete User A's comment

**Expected Response (403):**
```json
{
  "detail": "You do not have permission to modify this comment"
}
```

**Note**: Admin and Manager roles can modify other users' content.

---

## Step 14: Error Handling Tests

### Test Non-Existing Decision (404)

**Endpoint**: `POST /decisions/99999/comments`

**Request Body:**
```json
{
  "content": "This should fail"
}
```

**Expected Response (404):**
```json
{
  "detail": "Decision not found"
}
```

---

### Test Non-Existing Comment (404)

**Endpoint**: `GET /comments/99999`

**Expected Response (404):**
```json
{
  "detail": "Comment not found"
}
```

---

### Test Non-Existing Thread (404)

**Endpoint**: `GET /threads/99999`

**Expected Response (404):**
```json
{
  "detail": "Discussion thread not found"
}
```

---

### Test Missing Required Field (422)

**Endpoint**: `POST /decisions/{decision_id}/comments`

**Request Body (missing 'content' field):**
```json
{}
```

**Expected Response (422):**
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

## Step 15: Complete Workflow Summary

By this point, you should have demonstrated:

1. ✅ User authentication (login)
2. ✅ Decision creation
3. ✅ Comment creation (3 comments)
4. ✅ Comment retrieval (list)
5. ✅ Single comment retrieval
6. ✅ Comment update
7. ✅ Comment deletion (test with one comment)
8. ✅ Discussion thread creation
9. ✅ Thread replies
10. ✅ Meeting notes creation
11. ✅ Decision rationale recording
12. ✅ Authentication failure (401)
13. ✅ Authorization failure (403)
14. ✅ Not found errors (404)
15. ✅ Validation errors (422)

---

## Bonus: Retrieve All Resources

### Get all discussions threads for a decision
**Endpoint**: `GET /decisions/{decision_id}/threads`

### Get all meeting notes for a decision
**Endpoint**: `GET /decisions/{decision_id}/meeting-notes`

### Get specific meeting note
**Endpoint**: `GET /meeting-notes/{note_id}`

### Get specific thread
**Endpoint**: `GET /threads/{thread_id}`

### Get all replies to a thread
**Endpoint**: `GET /threads/{thread_id}/comments`

---

## Notes for Testing

1. **JWT Token**: Always include the bearer token in the Authorization header
2. **User ID**: The logged-in user's ID is automatically extracted from the JWT token
3. **Timestamps**: Dates are in ISO 8601 format with UTC timezone
4. **Ownership**: Only the comment/thread/note creator or admin can modify it
5. **Soft Deletion**: Comments are actually deleted, not soft-deleted
6. **Thread Status**: Can be "Open", "Resolved", or "Closed"

---

## Next Step: Database Verification

After testing the APIs, open pgAdmin and verify:
- `comments` table has entries
- `discussion_threads` table has entries
- `meeting_notes` table has entries
- All foreign keys are correctly set up
- Timestamps are accurate
- User IDs are correctly associated with records
