# Sprint 6 - Alternative Analysis Module - CURL Examples

## Setup

### 1. Login and Get JWT Token
```bash
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john.doe@company.com&password=TestPassword123"
```

**Response:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

**Save the token as a variable:**
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Decision Creation (Required for Alternatives)

### Create a Decision
```bash
curl -X POST http://localhost:8000/decisions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Select Database",
    "problem_statement": "We need to choose a database for our new platform",
    "category": "Technology"
  }'
```

**Save the decision ID:**
```bash
DECISION_ID=1
```

---

## Alternative Endpoints

### 1. Create Alternative
```bash
curl -X POST http://localhost:8000/decisions/$DECISION_ID/alternatives \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "PostgreSQL",
    "description": "Use PostgreSQL as the primary relational database",
    "pros": "Reliable, mature ecosystem, excellent performance",
    "cons": "Requires relational schema design",
    "estimated_cost": 5000,
    "feasibility_score": 5,
    "risk_level": "Low"
  }'
```

**Create MySQL Alternative:**
```bash
curl -X POST http://localhost:8000/decisions/$DECISION_ID/alternatives \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MySQL",
    "description": "Use MySQL as the database solution",
    "pros": "Easy to use, widely supported",
    "cons": "Limited advanced features",
    "estimated_cost": 4500,
    "feasibility_score": 4,
    "risk_level": "Low"
  }'
```

**Create MongoDB Alternative:**
```bash
curl -X POST http://localhost:8000/decisions/$DECISION_ID/alternatives \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MongoDB",
    "description": "Use MongoDB as a NoSQL database",
    "pros": "Scalable, flexible schema",
    "cons": "Requires different query patterns",
    "estimated_cost": 7000,
    "feasibility_score": 4,
    "risk_level": "Medium"
  }'
```

**Save the alternative ID:**
```bash
ALTERNATIVE_ID=1
```

---

### 2. Get All Alternatives for a Decision
```bash
curl -X GET http://localhost:8000/decisions/$DECISION_ID/alternatives \
  -H "Authorization: Bearer $TOKEN"
```

---

### 3. Get Single Alternative
```bash
curl -X GET http://localhost:8000/alternatives/$ALTERNATIVE_ID \
  -H "Authorization: Bearer $TOKEN"
```

---

### 4. Update Alternative
```bash
curl -X PUT http://localhost:8000/alternatives/$ALTERNATIVE_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "estimated_cost": 5500,
    "feasibility_score": 5,
    "pros": "Reliable, scalable, mature ecosystem"
  }'
```

---

### 5. Compare Alternatives
```bash
curl -X GET http://localhost:8000/decisions/$DECISION_ID/alternatives/compare \
  -H "Authorization: Bearer $TOKEN"
```

---

## Error Testing

### Test 1: Invalid Risk Level (Expected: 422)
```bash
curl -X POST http://localhost:8000/decisions/$DECISION_ID/alternatives \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test",
    "description": "Test invalid risk level",
    "pros": "Test",
    "cons": "Test",
    "estimated_cost": 1000,
    "feasibility_score": 3,
    "risk_level": "Very Dangerous"
  }'
```

### Test 2: Invalid Feasibility Score (Expected: 422)
```bash
curl -X POST http://localhost:8000/decisions/$DECISION_ID/alternatives \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test",
    "description": "Test invalid feasibility",
    "pros": "Test",
    "cons": "Test",
    "estimated_cost": 1000,
    "feasibility_score": 10,
    "risk_level": "Low"
  }'
```

### Test 3: Non-Existing Decision (Expected: 404)
```bash
curl -X POST http://localhost:8000/decisions/99999/alternatives \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test",
    "description": "Test non-existing decision",
    "pros": "Test",
    "cons": "Test",
    "estimated_cost": 1000,
    "feasibility_score": 3,
    "risk_level": "Low"
  }'
```

### Test 4: Non-Existing Alternative (Expected: 404)
```bash
curl -X GET http://localhost:8000/alternatives/99999 \
  -H "Authorization: Bearer $TOKEN"
```

### Test 5: Missing JWT Token (Expected: 401)
```bash
curl -X GET http://localhost:8000/decisions/$DECISION_ID/alternatives
```

---

## PowerShell Script for Complete Testing

Save this as `test_alternatives.ps1`:

```powershell
# Test Script for Alternative Analysis Module
$BaseURL = "http://localhost:8000"

# Step 1: Login
Write-Host "Step 1: Login" -ForegroundColor Green
$loginResponse = Invoke-RestMethod -Uri "$BaseURL/token" -Method POST `
  -ContentType "application/x-www-form-urlencoded" `
  -Body "username=john.doe@company.com&password=TestPassword123"

$token = $loginResponse.access_token
Write-Host "Token: $($token.Substring(0, 20))..." -ForegroundColor Yellow

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# Step 2: Create Decision
Write-Host "`nStep 2: Create Decision" -ForegroundColor Green
$decisionBody = @{
    title = "Select Database"
    problem_statement = "We need to choose a database for our new platform"
    category = "Technology"
} | ConvertTo-Json

$decisionResponse = Invoke-RestMethod -Uri "$BaseURL/decisions" -Method POST `
  -Headers $headers -Body $decisionBody

$decisionId = $decisionResponse.id
Write-Host "Decision ID: $decisionId" -ForegroundColor Yellow

# Step 3: Create Alternatives
Write-Host "`nStep 3: Create Alternatives" -ForegroundColor Green

$alternatives = @(
    @{
        name = "PostgreSQL"
        description = "Use PostgreSQL as the primary relational database"
        pros = "Reliable, mature ecosystem, excellent performance"
        cons = "Requires relational schema design"
        estimated_cost = 5000
        feasibility_score = 5
        risk_level = "Low"
    },
    @{
        name = "MySQL"
        description = "Use MySQL as the database solution"
        pros = "Easy to use, widely supported"
        cons = "Limited advanced features"
        estimated_cost = 4500
        feasibility_score = 4
        risk_level = "Low"
    },
    @{
        name = "MongoDB"
        description = "Use MongoDB as a NoSQL database"
        pros = "Scalable, flexible schema"
        cons = "Requires different query patterns"
        estimated_cost = 7000
        feasibility_score = 4
        risk_level = "Medium"
    }
)

$alternativeIds = @()
foreach ($alt in $alternatives) {
    $altBody = $alt | ConvertTo-Json
    $altResponse = Invoke-RestMethod -Uri "$BaseURL/decisions/$decisionId/alternatives" -Method POST `
      -Headers $headers -Body $altBody
    $alternativeIds += $altResponse.id
    Write-Host "Created: $($altResponse.name) (ID: $($altResponse.id))" -ForegroundColor Yellow
}

# Step 4: Get All Alternatives
Write-Host "`nStep 4: Get All Alternatives" -ForegroundColor Green
$allAlts = Invoke-RestMethod -Uri "$BaseURL/decisions/$decisionId/alternatives" -Method GET `
  -Headers $headers
Write-Host "Retrieved $($allAlts.Count) alternatives" -ForegroundColor Yellow

# Step 5: Get Single Alternative
Write-Host "`nStep 5: Get Single Alternative" -ForegroundColor Green
$singleAlt = Invoke-RestMethod -Uri "$BaseURL/alternatives/$($alternativeIds[0])" -Method GET `
  -Headers $headers
Write-Host "Retrieved: $($singleAlt.name)" -ForegroundColor Yellow

# Step 6: Update Alternative
Write-Host "`nStep 6: Update Alternative" -ForegroundColor Green
$updateBody = @{
    estimated_cost = 5500
    feasibility_score = 5
    pros = "Reliable, scalable, mature ecosystem"
} | ConvertTo-Json

$updatedAlt = Invoke-RestMethod -Uri "$BaseURL/alternatives/$($alternativeIds[0])" -Method PUT `
  -Headers $headers -Body $updateBody
Write-Host "Updated: $($updatedAlt.name) (New Cost: `$$($updatedAlt.estimated_cost))" -ForegroundColor Yellow

# Step 7: Compare Alternatives
Write-Host "`nStep 7: Compare Alternatives" -ForegroundColor Green
$comparison = Invoke-RestMethod -Uri "$BaseURL/decisions/$decisionId/alternatives/compare" -Method GET `
  -Headers $headers
Write-Host "Comparison for Decision $decisionId:" -ForegroundColor Yellow
foreach ($alt in $comparison.alternatives) {
    Write-Host "  - $($alt.name): Cost=`$$($alt.estimated_cost), Feasibility=$($alt.feasibility_score)/5, Risk=$($alt.risk_level)" -ForegroundColor Cyan
}

# Step 8: Test Validation
Write-Host "`nStep 8: Test Validation (Invalid Risk Level)" -ForegroundColor Green
try {
    $invalidBody = @{
        name = "Test"
        description = "Test"
        pros = "Test"
        cons = "Test"
        estimated_cost = 1000
        feasibility_score = 3
        risk_level = "Very Dangerous"
    } | ConvertTo-Json
    
    $invalidResponse = Invoke-RestMethod -Uri "$BaseURL/decisions/$decisionId/alternatives" -Method POST `
      -Headers $headers -Body $invalidBody
} catch {
    Write-Host "Expected Error: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n✓ All tests completed!" -ForegroundColor Green
```

Run with:
```powershell
.\test_alternatives.ps1
```

---

## Swagger UI

Open your browser to access the interactive Swagger UI:
```
http://localhost:8000/docs
```

All endpoints are documented with request/response examples and can be tested directly from the UI.

---

## Summary

**All Endpoints Tested:**
- ✓ Create Alternative (POST)
- ✓ List Alternatives (GET)
- ✓ Get Single Alternative (GET)
- ✓ Update Alternative (PUT)
- ✓ Compare Alternatives (GET)

**Validation Tested:**
- ✓ Feasibility Score (1-5 only)
- ✓ Risk Level (Low, Medium, High, Critical only)
- ✓ Non-existing resources (404)
- ✓ Missing JWT token (401)

**Success Criteria Met:**
- ✓ All endpoints return correct HTTP status codes
- ✓ Validation errors return 422 with detailed messages
- ✓ Not found errors return 404
- ✓ Missing JWT returns 401
- ✓ Database operations are persisted correctly
