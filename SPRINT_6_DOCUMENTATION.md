# Sprint 6 – Alternative Analysis Module

## Overview
The Alternative Analysis Module enables users to associate multiple alternatives with a single decision and compare them based on key criteria: cost, feasibility, and risk.

## Database Schema

### Alternative Table
```sql
CREATE TABLE alternatives (
    id SERIAL PRIMARY KEY,
    decision_id INTEGER NOT NULL REFERENCES decisions(id),
    name VARCHAR NOT NULL,
    description TEXT NOT NULL,
    pros TEXT NOT NULL,
    cons TEXT NOT NULL,
    estimated_cost INTEGER NOT NULL,
    feasibility_score INTEGER NOT NULL CHECK (feasibility_score BETWEEN 1 AND 5),
    risk_level VARCHAR NOT NULL CHECK (risk_level IN ('Low', 'Medium', 'High', 'Critical')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Relationships
- **One Decision → Many Alternatives** (One-to-Many)
- Foreign key: `alternatives.decision_id` → `decisions.id`
- Cascade delete enabled

## API Endpoints

### 1. Create Alternative
**Endpoint:** `POST /decisions/{decision_id}/alternatives`

**Authentication:** Required (JWT)

**Request Body:**
```json
{
    "name": "PostgreSQL",
    "description": "Use PostgreSQL as the primary relational database",
    "pros": "Reliable, mature ecosystem, excellent performance",
    "cons": "Requires relational schema design",
    "estimated_cost": 5000,
    "feasibility_score": 5,
    "risk_level": "Low"
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "decision_id": 1,
    "name": "PostgreSQL",
    "description": "Use PostgreSQL as the primary relational database",
    "pros": "Reliable, mature ecosystem, excellent performance",
    "cons": "Requires relational schema design",
    "estimated_cost": 5000,
    "feasibility_score": 5,
    "risk_level": "Low",
    "created_at": "2026-08-18T19:30:00+00:00",
    "updated_at": "2026-08-18T19:30:00+00:00"
}
```

**Error Responses:**
- `404 Not Found`: Decision doesn't exist
  ```json
  {
      "detail": "Decision not found"
  }
  ```
- `422 Unprocessable Entity`: Invalid feasibility_score or risk_level
  ```json
  {
      "detail": [
          {
              "type": "value_error",
              "loc": ["body", "feasibility_score"],
              "msg": "feasibility_score must be an integer between 1 and 5"
          }
      ]
  }
  ```
- `401 Unauthorized`: Missing or invalid JWT

### 2. Get All Alternatives for a Decision
**Endpoint:** `GET /decisions/{decision_id}/alternatives`

**Authentication:** Required (JWT)

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "decision_id": 1,
        "name": "PostgreSQL",
        "description": "Use PostgreSQL as the primary relational database",
        "pros": "Reliable, mature ecosystem, excellent performance",
        "cons": "Requires relational schema design",
        "estimated_cost": 5000,
        "feasibility_score": 5,
        "risk_level": "Low",
        "created_at": "2026-08-18T19:30:00+00:00",
        "updated_at": "2026-08-18T19:30:00+00:00"
    },
    {
        "id": 2,
        "decision_id": 1,
        "name": "MySQL",
        "description": "Use MySQL as the database solution",
        "pros": "Easy to use, widely supported",
        "cons": "Limited advanced features",
        "estimated_cost": 4500,
        "feasibility_score": 4,
        "risk_level": "Low",
        "created_at": "2026-08-18T19:31:00+00:00",
        "updated_at": "2026-08-18T19:31:00+00:00"
    }
]
```

**Error Responses:**
- `404 Not Found`: Decision doesn't exist
- `401 Unauthorized`: Missing or invalid JWT

### 3. Get Single Alternative
**Endpoint:** `GET /alternatives/{alternative_id}`

**Authentication:** Required (JWT)

**Response (200 OK):**
```json
{
    "id": 1,
    "decision_id": 1,
    "name": "PostgreSQL",
    "description": "Use PostgreSQL as the primary relational database",
    "pros": "Reliable, mature ecosystem, excellent performance",
    "cons": "Requires relational schema design",
    "estimated_cost": 5000,
    "feasibility_score": 5,
    "risk_level": "Low",
    "created_at": "2026-08-18T19:30:00+00:00",
    "updated_at": "2026-08-18T19:30:00+00:00"
}
```

**Error Responses:**
- `404 Not Found`: Alternative doesn't exist
- `401 Unauthorized`: Missing or invalid JWT

### 4. Update Alternative
**Endpoint:** `PUT /alternatives/{alternative_id}`

**Authentication:** Required (JWT)

**Request Body (all fields optional):**
```json
{
    "name": "PostgreSQL",
    "description": "Updated description",
    "pros": "Reliable, scalable, mature ecosystem",
    "cons": "Requires relational schema design",
    "estimated_cost": 5500,
    "feasibility_score": 5,
    "risk_level": "Low"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "decision_id": 1,
    "name": "PostgreSQL",
    "description": "Updated description",
    "pros": "Reliable, scalable, mature ecosystem",
    "cons": "Requires relational schema design",
    "estimated_cost": 5500,
    "feasibility_score": 5,
    "risk_level": "Low",
    "created_at": "2026-08-18T19:30:00+00:00",
    "updated_at": "2026-08-18T19:40:00+00:00"
}
```

**Error Responses:**
- `404 Not Found`: Alternative doesn't exist
- `422 Unprocessable Entity`: Invalid feasibility_score or risk_level
- `401 Unauthorized`: Missing or invalid JWT

### 5. Compare Alternatives
**Endpoint:** `GET /decisions/{decision_id}/alternatives/compare`

**Authentication:** Required (JWT)

**Response (200 OK):**
```json
{
    "decision_id": 1,
    "alternatives": [
        {
            "name": "PostgreSQL",
            "estimated_cost": 5000,
            "feasibility_score": 5,
            "risk_level": "Low"
        },
        {
            "name": "MySQL",
            "estimated_cost": 4500,
            "feasibility_score": 4,
            "risk_level": "Low"
        },
        {
            "name": "MongoDB",
            "estimated_cost": 7000,
            "feasibility_score": 4,
            "risk_level": "Medium"
        }
    ]
}
```

**Error Responses:**
- `404 Not Found`: Decision doesn't exist
- `401 Unauthorized`: Missing or invalid JWT

## Business Rules & Validation

### Feasibility Score
- **Allowed Values:** 1-5 (integer only)
- **Meaning:**
  - 1 = Very difficult
  - 2 = Difficult
  - 3 = Moderate
  - 4 = Good
  - 5 = Very feasible
- **Validation Error:** Any value outside 1-5 returns 422 with detailed error

### Risk Level
- **Allowed Values:** `Low`, `Medium`, `High`, `Critical`
- **Case-Sensitive:** Values must match exactly
- **Validation Error:** Any other value returns 422 with detailed error

### Estimated Cost
- **Type:** Integer
- **Unit:** Currency (typically USD)
- **No Validation:** Any positive or negative integer is accepted

### Protected Fields
Cannot be modified after creation:
- `id` (Primary key)
- `decision_id` (Foreign key)
- `created_at` (Timestamp)

Can be updated:
- `name`
- `description`
- `pros`
- `cons`
- `estimated_cost`
- `feasibility_score`
- `risk_level`
- `updated_at` (automatically updated)

## Authentication & Authorization

### JWT Token
- All endpoints require valid JWT token in `Authorization` header
- Format: `Authorization: Bearer <token>`
- Token obtained via `/token` endpoint with email/password credentials

### Missing Token
- Response: `401 Unauthorized`
- Headers: Must include `Authorization: Bearer <JWT_TOKEN>`

### Invalid Token
- Response: `401 Unauthorized`

## Error Handling

### 400 Bad Request
Not used for alternatives endpoints

### 401 Unauthorized
- Missing JWT token
- Invalid JWT token
- Expired JWT token

### 404 Not Found
- Decision doesn't exist (when creating/listing alternatives)
- Alternative doesn't exist (when retrieving/updating)

### 422 Unprocessable Entity
- `feasibility_score` outside 1-5 range
- `risk_level` not in (`Low`, `Medium`, `High`, `Critical`)
- Missing required field

### 500 Internal Server Error
- Database connection issues
- Unexpected server errors

## Testing Workflow

### Step 1: Login
```bash
POST /token
Content-Type: application/x-www-form-urlencoded

username=john.doe@company.com&password=TestPassword123
```

### Step 2: Create Decision
```bash
POST /decisions
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
    "title": "Select Database",
    "problem_statement": "We need to choose a database for our new platform",
    "category": "Technology"
}
```

### Step 3: Create Alternatives
```bash
POST /decisions/1/alternatives
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
    "name": "PostgreSQL",
    "description": "Use PostgreSQL as the primary relational database",
    "pros": "Reliable, mature ecosystem, excellent performance",
    "cons": "Requires relational schema design",
    "estimated_cost": 5000,
    "feasibility_score": 5,
    "risk_level": "Low"
}
```

### Step 4: List Alternatives
```bash
GET /decisions/1/alternatives
Authorization: Bearer <JWT_TOKEN>
```

### Step 5: Get Single Alternative
```bash
GET /alternatives/1
Authorization: Bearer <JWT_TOKEN>
```

### Step 6: Update Alternative
```bash
PUT /alternatives/1
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
    "estimated_cost": 5500,
    "feasibility_score": 5
}
```

### Step 7: Compare Alternatives
```bash
GET /decisions/1/alternatives/compare
Authorization: Bearer <JWT_TOKEN>
```

### Step 8: Test Validation (Expected: 422)
```bash
POST /decisions/1/alternatives
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
    "name": "Test",
    "description": "Test",
    "pros": "Test",
    "cons": "Test",
    "estimated_cost": 1000,
    "feasibility_score": 10,  # Invalid: must be 1-5
    "risk_level": "Low"
}
```

## Database Verification (pgAdmin)

### Table Structure
1. Open pgAdmin
2. Navigate to: Databases → expert_decision_replay → Schemas → public → Tables
3. Verify `alternatives` table exists with columns:
   - id (SERIAL, PRIMARY KEY)
   - decision_id (INTEGER, FOREIGN KEY)
   - name (VARCHAR)
   - description (TEXT)
   - pros (TEXT)
   - cons (TEXT)
   - estimated_cost (INTEGER)
   - feasibility_score (INTEGER)
   - risk_level (VARCHAR)
   - created_at (TIMESTAMP WITH TIME ZONE)
   - updated_at (TIMESTAMP WITH TIME ZONE)

### Foreign Key Verification
1. Right-click `alternatives` table → Properties
2. Go to Constraints tab
3. Verify foreign key constraint:
   - Table: alternatives
   - Column: decision_id
   - References: decisions(id)

### Data Verification
1. Right-click `alternatives` table → View/Edit Data
2. Verify alternatives are stored correctly
3. Verify decision_id references are correct
4. Verify updated_at is modified when alternatives are updated

## Implementation Files

### Models
- `app/models/alternative.py` - SQLAlchemy model for Alternative

### Schemas
- `app/schemas/alternative.py` - Pydantic schemas for request/response

### Routers
- `routers/alternative.py` - API endpoints

### Migrations
- `alembic/versions/a1b2c3d4e5f6_create_alternatives_table.py` - Database migration

### Main Application
- `app/main.py` - Updated to include alternative routers

## Summary of Features Implemented

✅ **SQLAlchemy Model**
- Alternative model with all required fields
- Relationship to Decision (cascade delete)

✅ **Database Migration**
- Alembic migration created and applied
- Alternatives table with proper schema and constraints

✅ **Pydantic Schemas**
- AlternativeCreate: For creating alternatives
- AlternativeUpdate: For updating alternatives
- AlternativeResponse: For API responses
- AlternativeComparison: For comparison endpoint

✅ **API Endpoints**
- POST /decisions/{decision_id}/alternatives (Create)
- GET /decisions/{decision_id}/alternatives (List)
- GET /alternatives/{alternative_id} (Get by ID)
- PUT /alternatives/{alternative_id} (Update)
- GET /decisions/{decision_id}/alternatives/compare (Compare)

✅ **Validation**
- Feasibility score (1-5)
- Risk level (Low, Medium, High, Critical)
- Required fields validation
- 404 handling for non-existent resources

✅ **Authentication & Authorization**
- JWT token required on all endpoints
- Uses existing authentication system from app/core/auth.py
- 401 returned for missing/invalid tokens

✅ **Error Handling**
- Proper HTTP status codes (201, 200, 404, 422, 401)
- Detailed error messages
- Validation error details

## Testing

Run the comprehensive test suite:
```bash
python test_alternatives_sprint6.py
```

Expected output: All tests pass with proper status codes and error handling.

## Git Workflow

1. Add all files:
   ```bash
   git add .
   ```

2. Commit with descriptive message:
   ```bash
   git commit -m "Sprint 6: Implement Alternative Analysis Module

   - Create Alternative SQLAlchemy model
   - Add Alembic migration for alternatives table
   - Implement Pydantic schemas for alternatives
   - Create API endpoints for CRUD operations
   - Add alternative comparison endpoint
   - Implement business rule validation
   - Add comprehensive test suite"
   ```

3. Push to remote:
   ```bash
   git push origin main
   ```

## Notes for Future Sprints

- **Sprint 7**: Implement approval workflow for alternatives
- **Sprint 8**: Add advanced filtering and sorting
- **Sprint 9**: Implement weighted scoring for alternatives
- **Sprint 10**: Add analytics and reporting for alternatives
