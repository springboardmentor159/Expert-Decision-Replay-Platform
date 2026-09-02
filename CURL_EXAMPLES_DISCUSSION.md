# Discussion and Collaboration Module - CURL Examples

## Authentication

### Login
```bash
curl -X POST "http://127.0.0.1:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password123"
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Save the access_token for use in all subsequent requests.**

---

## Set JWT Token Variable

```bash
# For Windows PowerShell:
$TOKEN = "your_access_token_here"

# For bash/Linux:
TOKEN="your_access_token_here"
```

---

## Comments API Examples

### 1. Create a Comment
```bash
curl -X POST "http://127.0.0.1:8000/decisions/1/comments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "PostgreSQL provides strong relational support and has mature tooling."
  }'
```

### 2. Get All Comments for a Decision
```bash
curl -X GET "http://127.0.0.1:8000/decisions/1/comments" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Get Specific Comment
```bash
curl -X GET "http://127.0.0.1:8000/comments/1" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Update a Comment
```bash
curl -X PUT "http://127.0.0.1:8000/comments/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Updated: PostgreSQL is the best choice for our use case."
  }'
```

### 5. Delete a Comment
```bash
curl -X DELETE "http://127.0.0.1:8000/comments/1" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Discussion Threads API Examples

### 1. Create a Discussion Thread
```bash
curl -X POST "http://127.0.0.1:8000/decisions/1/threads" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Database Scalability",
    "description": "Let'\''s discuss the scalability requirements before finalizing the database choice."
  }'
```

### 2. Get All Threads for a Decision
```bash
curl -X GET "http://127.0.0.1:8000/decisions/1/threads" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Get Specific Thread
```bash
curl -X GET "http://127.0.0.1:8000/threads/1" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Update Thread
```bash
curl -X PUT "http://127.0.0.1:8000/threads/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Database Scalability & Performance",
    "description": "Updated discussion about scalability.",
    "status": "Resolved"
  }'
```

### 5. Delete Thread
```bash
curl -X DELETE "http://127.0.0.1:8000/threads/1" \
  -H "Authorization: Bearer $TOKEN"
```

### 6. Add Reply to Thread
```bash
curl -X POST "http://127.0.0.1:8000/threads/1/comments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "PostgreSQL can handle millions of rows efficiently with proper indexing."
  }'
```

### 7. Get All Replies to Thread
```bash
curl -X GET "http://127.0.0.1:8000/threads/1/comments" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Meeting Notes API Examples

### 1. Create Meeting Note
```bash
curl -X POST "http://127.0.0.1:8000/decisions/1/meeting-notes" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Database Selection Meeting - January 15",
    "content": "Team discussed three database options. Consensus was PostgreSQL.",
    "meeting_date": "2025-01-15T14:00:00"
  }'
```

### 2. Get All Meeting Notes for Decision
```bash
curl -X GET "http://127.0.0.1:8000/decisions/1/meeting-notes" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Get Specific Meeting Note
```bash
curl -X GET "http://127.0.0.1:8000/meeting-notes/1" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Update Meeting Note
```bash
curl -X PUT "http://127.0.0.1:8000/meeting-notes/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Database Selection Meeting - January 15 (Final)",
    "content": "Final decision: PostgreSQL selected with additional recommendations.",
    "meeting_date": "2025-01-15T15:00:00"
  }'
```

### 5. Delete Meeting Note
```bash
curl -X DELETE "http://127.0.0.1:8000/meeting-notes/1" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Decision Rationale API Examples

### Update Decision Rationale
```bash
curl -X PUT "http://127.0.0.1:8000/decisions/1/rationale" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rationale": "PostgreSQL was selected because it provided the best balance between reliability, feasibility, cost, and operational risk."
  }'
```

---

## Error Testing Examples

### Test Unauthorized Access (No JWT)
```bash
curl -X GET "http://127.0.0.1:8000/decisions/1/comments"
```

Expected: 401 Unauthorized

---

### Test Non-Existing Resource (404)
```bash
curl -X GET "http://127.0.0.1:8000/comments/99999" \
  -H "Authorization: Bearer $TOKEN"
```

Expected: 404 Not Found

---

### Test Non-Existing Decision
```bash
curl -X POST "http://127.0.0.1:8000/decisions/99999/comments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "This should fail"}'
```

Expected: 404 Not Found

---

### Test Validation Error (Missing Required Field)
```bash
curl -X POST "http://127.0.0.1:8000/decisions/1/comments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Expected: 422 Validation Error

---

## PowerShell Examples

### PowerShell Script for Testing

```powershell
# Set variables
$baseUrl = "http://127.0.0.1:8000"
$email = "user@example.com"
$password = "password123"

# 1. Login
$loginResponse = Invoke-RestMethod -Uri "$baseUrl/token" -Method Post `
  -ContentType "application/x-www-form-urlencoded" `
  -Body "username=$email&password=$password"

$token = $loginResponse.access_token
$headers = @{"Authorization" = "Bearer $token"}

# 2. Create decision
$decisionBody = @{
    title = "Select Database for New Project"
    problem_statement = "We need to choose a database for our microservices"
    category = "Technology"
} | ConvertTo-Json

$decisionResponse = Invoke-RestMethod -Uri "$baseUrl/decisions" -Method Post `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $decisionBody

$decisionId = $decisionResponse.id

# 3. Create comment
$commentBody = @{
    content = "PostgreSQL provides strong relational support"
} | ConvertTo-Json

$commentResponse = Invoke-RestMethod -Uri "$baseUrl/decisions/$decisionId/comments" `
  -Method Post -Headers $headers -ContentType "application/json" -Body $commentBody

Write-Host "Created comment with ID: $($commentResponse.id)"

# 4. Get all comments
$comments = Invoke-RestMethod -Uri "$baseUrl/decisions/$decisionId/comments" `
  -Method Get -Headers $headers

Write-Host "Total comments: $($comments.Count)"
$comments | ForEach-Object { Write-Host "- $($_.content)" }
```

---

## Testing Workflow

1. **Login and get token**
2. **Create a decision**
3. **Create 3 comments**
4. **Get all comments**
5. **Get specific comment**
6. **Update a comment**
7. **Create discussion thread**
8. **Add replies to thread**
9. **Create meeting notes**
10. **Update decision rationale**
11. **Test error cases**

---

## Tips

- Replace `$TOKEN` with your actual access token
- Replace `1`, `2`, etc. with actual IDs from your API responses
- Use `jq` (on Linux/Mac) to format JSON responses: `| jq .`
- Use PowerShell's `ConvertTo-Json` for formatting
- Always check the response status code for errors
