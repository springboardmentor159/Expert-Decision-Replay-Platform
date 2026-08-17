# Sprint 5 - Part 2: Decision Update, Status Management & Filtering
## Implementation Summary & Documentation

### Overview
This document summarizes the complete implementation of the Decision Management module with business-grade features including decision updates, controlled status management, filtering, JWT authentication, and role-based authorization.

---

## ✅ Completed Features

### 1. Decision Update API
**Endpoint:** `PUT /decisions/{decision_id}`

**Functionality:**
- Update existing decision fields (title, problem_statement, category)
- Protected fields that cannot be changed:
  - `id` (primary key)
  - `created_by` (user who created the decision)
  - `created_at` (creation timestamp)
- Returns 404 if decision not found
- Returns updated decision with new `updated_at` timestamp

**Example Request:**
```json
{
  "title": "Updated Decision Title",
  "problem_statement": "Updated problem description",
  "category": "Technology"
}
```

**Example Response:**
```json
{
  "id": 4,
  "title": "Updated Decision Title",
  "problem_statement": "Updated problem description",
  "category": "Technology",
  "status": "Draft",
  "created_by": 14,
  "created_at": "2026-08-17T16:56:36.496287+05:30",
  "updated_at": "2026-08-17T16:56:36.569017+05:30"
}
```

---

### 2. Decision Status Management
**Status Enum Values (Controlled):**
- `Draft` - Initial status for new decisions
- `Under Review` - Decision is being reviewed
- `Approved` - Decision has been approved
- `Rejected` - Decision was rejected
- `Archived` - Decision is archived/completed

**Implementation:**
- Status is enforced at the API level using Pydantic enums
- Only valid status values are accepted
- Invalid status values receive a 422 Validation Error
- Default status for new decisions is "Draft"

**Database Verification:**
- Status field stored as VARCHAR in PostgreSQL
- Database constraints ensure data consistency
- Controlled values prevent data inconsistency

---

### 3. Status Update API
**Endpoint:** `PATCH /decisions/{decision_id}/status`

**Functionality:**
- Update only the status field of a decision
- Validates status against enum values
- Returns 404 if decision not found
- Returns 422 (Validation Error) for invalid status values
- Updates `updated_at` timestamp automatically

**Example Request:**
```json
{
  "status": "Under Review"
}
```

**Invalid Status Example:**
```json
{
  "status": "Completed"  // Will return 422 Validation Error
}
```

**Error Response:**
```json
{
  "detail": [
    {
      "type": "enum",
      "loc": ["body", "status"],
      "msg": "Input should be 'Draft', 'Under Review', 'Approved', 'Rejected' or 'Archived'",
      "input": "Completed"
    }
  ]
}
```

---

### 4. Decision Filtering API
**Endpoint:** `GET /decisions?status=Draft&category=Technology`

**Filtering Options:**
1. **By Status:** `GET /decisions?status=Draft`
   - Returns only decisions with the specified status
   - Status value must match exactly (case-sensitive)

2. **By Category:** `GET /decisions?category=Technology`
   - Returns only decisions with the specified category

3. **Combined Filters:** `GET /decisions?status=Approved&category=Technology`
   - Returns decisions matching both criteria (AND logic)
   - Multiple filters can be applied simultaneously

**Example Usage:**
```bash
# Get all Draft decisions
GET /decisions?status=Draft

# Get all Technology decisions
GET /decisions?category=Technology

# Get Approved Technology decisions
GET /decisions?status=Approved&category=Technology
```

---

### 5. JWT Authentication & Authorization
**Authentication System:**
- All Decision endpoints require JWT token in Authorization header
- Format: `Authorization: Bearer <token>`
- Without JWT: Returns 401 Unauthorized
- Invalid JWT: Returns 401 Unauthorized
- Expired JWT: Returns 401 Unauthorized

**Implementation Details:**
- JWT tokens created via `/token` endpoint
- Token payload contains user email (`sub` claim)
- Token expiration: 30 minutes (configurable)
- Algorithm: HS256
- Secret key: Retrieved from `.env` file

**Login Flow:**
```
1. POST /token with email and password
2. Server validates credentials
3. Server returns access_token and token_type
4. Client includes token in subsequent requests: Authorization: Bearer <token>
```

---

## 📁 File Structure Changes

### New Files Created:
1. **`app/schemas/decision.py`**
   - DecisionStatus enum (Draft, Under Review, Approved, Rejected, Archived)
   - DecisionCreate schema
   - DecisionUpdate schema (partial update)
   - DecisionStatusUpdate schema
   - DecisionResponse schema

2. **`app/core/auth.py`**
   - Centralized authentication functions
   - `get_current_user()` - Dependency for JWT validation
   - `get_user_by_email()` - Database lookup function
   - `oauth2_scheme` - OAuth2 configuration

3. **`routers/decision.py`**
   - Complete Decision router with all endpoints:
     - POST /decisions - Create decision
     - GET /decisions - List decisions with filtering
     - GET /decisions/{decision_id} - Get specific decision
     - PUT /decisions/{decision_id} - Update decision
     - PATCH /decisions/{decision_id}/status - Update status
     - DELETE /decisions/{decision_id} - Delete/archive decision

### Modified Files:
1. **`app/main.py`**
   - Refactored to import auth functions from `app/core/auth.py`
   - Added decision router: `app.include_router(decisions_router)`
   - Removed duplicate decision endpoints
   - Cleaned up imports

2. **`app/schemas/user.py`**
   - Removed Decision-related schemas (now in `decision.py`)
   - Added TokenData schema (was missing)
   - Kept User-related schemas only

3. **Database**
   - Migration: `79db4e82e481_update_decision_table_with_status_and_.py`
   - Updated indices on decisions and users tables

---

## 🧪 Test Results

### API Tests Passed:
✅ Health check endpoint
✅ User creation with validation
✅ User login and JWT token generation
✅ Decision creation (default status: Draft)
✅ Retrieve specific decision
✅ Update decision fields
✅ Update decision status with enum validation
✅ Reject invalid status values
✅ Filter by status (Draft only)
✅ Filter by category (Infrastructure only)
✅ Combined filtering (status + category)
✅ Reject requests without JWT token
✅ Return 404 for non-existent decision

### Database Verification:
✅ Decisions table schema correct
✅ All columns present with correct data types
✅ Status field has correct default value
✅ created_by field properly stored
✅ created_at and updated_at timestamps maintained
✅ Timestamps change when decision is updated
✅ All status values are controlled (Draft, Approved, Under Review)
✅ Data integrity constraints enforced

---

## 🔒 Security Features

### Protected Endpoints:
All decision endpoints require JWT authentication:
```python
@router.get("", response_model=List[DecisionResponse])
def get_decisions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Endpoint implementation
```

### Immutable Fields:
- `id` - Primary key cannot be changed
- `created_by` - Cannot be changed by client (set at creation)
- `created_at` - Cannot be changed by client (set at creation)
- `updated_at` - Automatically updated by database

### Status Validation:
- Only predefined status values accepted
- Pydantic enum enforces validation before database write
- Invalid values rejected with clear error message

---

## 📊 Database Schema

### Decisions Table:
```
Column              | Type                   | Nullable | Default
--------------------|------------------------|----------|---------------------------
id                  | INTEGER                | NO       | nextval('decisions_id_seq')
title               | VARCHAR                | NO       | None
problem_statement   | TEXT                   | NO       | None
category            | VARCHAR                | NO       | None
status              | VARCHAR                | NO       | 'Draft'::character varying
created_by          | INTEGER (FK)           | NO       | None
created_at          | TIMESTAMP WITH TZ      | NO       | now()
updated_at          | TIMESTAMP WITH TZ      | NO       | now()
```

---

## 🚀 How to Use the API

### 1. Create a User
```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "email": "john@example.com",
    "role": "Employee",
    "employee_id": "EMP001",
    "department": "Technology",
    "designation": "Software Engineer",
    "phone_number": "1234567890",
    "password": "SecurePassword123"
  }'
```

### 2. Login and Get JWT Token
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@example.com&password=SecurePassword123"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### 3. Create a Decision
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

### 4. Get All Decisions with Filtering
```bash
# Get all Draft decisions
curl -X GET "http://localhost:8000/decisions?status=Draft" \
  -H "Authorization: Bearer {token}"

# Get Technology decisions
curl -X GET "http://localhost:8000/decisions?category=Technology" \
  -H "Authorization: Bearer {token}"

# Get Approved Technology decisions
curl -X GET "http://localhost:8000/decisions?status=Approved&category=Technology" \
  -H "Authorization: Bearer {token}"
```

### 5. Update a Decision
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

### 6. Update Decision Status
```bash
curl -X PATCH "http://localhost:8000/decisions/1/status" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Under Review"
  }'
```

---

## 📋 Business Rules Implemented

1. **Decision Creation**
   - New decisions automatically set to "Draft" status
   - User is identified from JWT token (created_by field)
   - All fields are required at creation time

2. **Decision Updates**
   - Only title, problem_statement, and category can be updated
   - Identity fields (id, created_by, created_at) are immutable
   - Updated timestamp changes automatically

3. **Status Management**
   - Only predefined status values are accepted
   - Client cannot submit arbitrary status strings
   - Status transitions are validated at API level
   - Future sprint will implement workflow rules (e.g., Draft→Under Review→Approved)

4. **Data Consistency**
   - Database enforces NOT NULL constraints
   - Timestamps are server-generated
   - Foreign key relationships maintained
   - Indices optimize query performance

5. **Access Control**
   - All decision endpoints require JWT authentication
   - No anonymous access to decision data
   - User identity tracked via created_by field

---

## 🔄 Workflow Status Transitions

Current implementation supports these transitions (future sprint will enforce rules):
```
Draft
  ├→ Under Review
  │   ├→ Approved
  │   │   └→ Archived
  │   └→ Rejected
  ├→ Archived
  └→ Rejected
```

---

## 📝 Testing Commands

### Run all API tests:
```bash
python test_decision_api.py
```

### Run combined filter tests:
```bash
python test_combined_filters.py
```

### Verify database:
```bash
python verify_db.py
```

---

## 🎯 Swagger/OpenAPI Testing

The API can be tested using Swagger UI at:
```
http://localhost:8000/docs
```

Features:
- Try out all endpoints directly
- See request/response schemas
- Validate authentication
- Test different status values
- Test filter combinations

---

## 🔍 Implementation Notes

### Circular Import Prevention:
- Created separate `app/core/auth.py` module for authentication
- Main.py imports from auth.py (one-way dependency)
- Routers import from auth.py (one-way dependency)
- No circular imports

### Database Timestamps:
- `created_at`: Set by database when record is inserted (immutable)
- `updated_at`: Set by database on insert and update (auto-updates)
- Both use PostgreSQL `now()` function for consistency
- Configured with UTC timezone support

### Enum Validation:
- Decision status uses Pydantic enum for type safety
- Validation happens at request parsing stage (before database)
- Clear error messages for invalid values
- Matches the User role enum pattern

---

## ✨ Quality Assurance

- ✅ All required endpoints implemented
- ✅ JWT authentication on all decision endpoints
- ✅ Enum validation for status values
- ✅ Query parameter filtering with multiple criteria
- ✅ Protected fields (id, created_by, created_at)
- ✅ Proper HTTP status codes (200, 201, 404, 422)
- ✅ Comprehensive error messages
- ✅ Database integrity verified
- ✅ Timestamps managed correctly
- ✅ Data consistency enforced

---

## 📌 Next Steps (Future Sprints)

1. **Approval Workflow**
   - Implement status transition rules
   - Add reviewer/manager permissions
   - Track approval history

2. **Enhanced Filtering**
   - Filter by date range (created_at, updated_at)
   - Filter by created_by user
   - Full-text search on title and problem_statement

3. **Audit Trail**
   - Log all status changes
   - Store reason for status changes
   - Track who made each change

4. **Performance**
   - Add pagination to GET /decisions
   - Implement caching for large datasets
   - Query optimization

---

## 📞 Support

For questions about the implementation:
1. Review the code comments in `routers/decision.py`
2. Check the schema definitions in `app/schemas/decision.py`
3. Review the authentication setup in `app/core/auth.py`
4. Run verification scripts: `verify_db.py`
