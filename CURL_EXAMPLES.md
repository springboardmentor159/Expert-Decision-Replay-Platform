# Quick Testing Examples - Decision Management API

## 🚀 Quick Start
Start the server first:
```bash
python main.py
```

Then in another terminal, run these examples:

---

## 1️⃣ LOGIN & GET TOKEN
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser@example.com&password=TestPassword123"
```

**Expected Response (Status 200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Copy the token and use it in the commands below as `{TOKEN}`**

---

## 2️⃣ CREATE A DECISION
```bash
TOKEN="your_token_here"

curl -X POST "http://localhost:8000/decisions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Migrate to PostgreSQL",
    "problem_statement": "Current SQLite has scalability issues",
    "category": "Technology"
  }'
```

**Expected Response (Status 201):**
```json
{
  "id": 1,
  "title": "Migrate to PostgreSQL",
  "problem_statement": "Current SQLite has scalability issues",
  "category": "Technology",
  "status": "Draft",
  "created_by": 14,
  "created_at": "2026-08-17T16:56:36.496287+05:30",
  "updated_at": "2026-08-17T16:56:36.496287+05:30"
}
```

**Note the status is "Draft" ✓**

---

## 3️⃣ GET ALL DECISIONS
```bash
TOKEN="your_token_here"

curl -X GET "http://localhost:8000/decisions" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (Status 200):**
```json
[
  {
    "id": 1,
    "title": "Migrate to PostgreSQL",
    ...
  }
]
```

---

## 4️⃣ GET SPECIFIC DECISION
```bash
TOKEN="your_token_here"

curl -X GET "http://localhost:8000/decisions/1" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (Status 200):**
```json
{
  "id": 1,
  "title": "Migrate to PostgreSQL",
  ...
}
```

---

## 5️⃣ UPDATE DECISION
```bash
TOKEN="your_token_here"

curl -X PUT "http://localhost:8000/decisions/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Migrate to PostgreSQL - Phase 1",
    "problem_statement": "Need scalable database solution",
    "category": "Infrastructure"
  }'
```

**Expected Response (Status 200):**
```json
{
  "id": 1,
  "title": "Migrate to PostgreSQL - Phase 1",
  "problem_statement": "Need scalable database solution",
  "category": "Infrastructure",
  "status": "Draft",
  "created_by": 14,
  "created_at": "2026-08-17T16:56:36.496287+05:30",
  "updated_at": "2026-08-17T16:57:00.123456+05:30"
}
```

**Important checks:**
- ✓ title changed ✓
- ✓ problem_statement changed ✓
- ✓ category changed ✓
- ✓ created_at DID NOT change ✓
- ✓ created_by DID NOT change ✓
- ✓ updated_at is NEWER ✓

---

## 6️⃣ UPDATE STATUS
```bash
TOKEN="your_token_here"

curl -X PATCH "http://localhost:8000/decisions/1/status" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Under Review"
  }'
```

**Expected Response (Status 200):**
```json
{
  "id": 1,
  ...
  "status": "Under Review",
  ...
}
```

**Note the status changed from "Draft" to "Under Review" ✓**

---

## 7️⃣ UPDATE STATUS TO APPROVED
```bash
TOKEN="your_token_here"

curl -X PATCH "http://localhost:8000/decisions/1/status" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Approved"
  }'
```

**Expected Response (Status 200):**
```json
{
  ...
  "status": "Approved",
  ...
}
```

---

## 8️⃣ TRY INVALID STATUS (Should Fail!)
```bash
TOKEN="your_token_here"

curl -X PATCH "http://localhost:8000/decisions/1/status" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Completed"
  }'
```

**Expected Response (Status 422 - Validation Error):**
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

✓ Invalid status correctly rejected!

---

## 9️⃣ FILTER BY STATUS
```bash
TOKEN="your_token_here"

curl -X GET "http://localhost:8000/decisions?status=Draft" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (Status 200):**
Returns only decisions with status="Draft"

---

## 🔟 FILTER BY CATEGORY
```bash
TOKEN="your_token_here"

curl -X GET "http://localhost:8000/decisions?category=Infrastructure" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (Status 200):**
Returns only decisions with category="Infrastructure"

---

## 1️⃣1️⃣ COMBINED FILTER (Status AND Category)
```bash
TOKEN="your_token_here"

curl -X GET "http://localhost:8000/decisions?status=Approved&category=Technology" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (Status 200):**
Returns only decisions with BOTH status="Approved" AND category="Technology"

---

## 1️⃣2️⃣ WITHOUT JWT TOKEN (Should Fail!)
```bash
curl -X GET "http://localhost:8000/decisions"
```

**Expected Response (Status 401 - Unauthorized):**
```json
{
  "detail": "Could not validate credentials"
}
```

✓ API correctly rejected request without JWT!

---

## 1️⃣3️⃣ NON-EXISTENT DECISION (Should Fail!)
```bash
TOKEN="your_token_here"

curl -X GET "http://localhost:8000/decisions/99999" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (Status 404 - Not Found):**
```json
{
  "detail": "Decision not found"
}
```

✓ API correctly returned 404 for non-existent decision!

---

## Valid Status Values (Controlled Enum)

Only these values are accepted:
- `Draft` - Initial status for new decisions
- `Under Review` - Decision is being reviewed
- `Approved` - Decision approved
- `Rejected` - Decision rejected
- `Archived` - Decision archived/completed

Any other value will be rejected with a validation error (422).

---

## Quick Checklist ✅

Run through these and verify:

- [ ] 1. Login returns a token
- [ ] 2. Create decision - status is "Draft"
- [ ] 3. Get all decisions returns list
- [ ] 4. Get specific decision works
- [ ] 5. Update decision - created_at unchanged, updated_at changed
- [ ] 6. Change status to "Under Review" works
- [ ] 7. Change status to "Approved" works
- [ ] 8. Invalid status "Completed" is rejected (422 error)
- [ ] 9. Filter by status=Draft returns only Draft
- [ ] 10. Filter by category works
- [ ] 11. Combined filters work
- [ ] 12. Without JWT returns 401
- [ ] 13. Non-existent ID returns 404

---

## Using Python Script

Instead of running these curl commands manually, you can run:

```bash
python examples_to_check.py
```

This will automatically run all 12 examples and show you the results!

---

## Swagger UI

You can also test in the browser at:
```
http://localhost:8000/docs
```

This shows an interactive API interface where you can try all endpoints!

---

## Database Check

To verify data is stored correctly in PostgreSQL:

```bash
python verify_db.py
```

This shows:
- Table schema
- Recent decisions
- Status values in database
- Timestamp verification
- Data integrity checks
