# Sprint 13 Step-by-Step API Test

This walkthrough tests the main decision lifecycle from Windows PowerShell. Run it against a test database, because it creates records.

## 1. Start the API

From the project folder:

```powershell
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

Open Swagger in a browser:

```text
http://127.0.0.1:8000/docs
```

Open a second PowerShell window for the requests below.

## 2. Set test variables

```powershell
$baseUrl = "http://127.0.0.1:8000"
$suffix = [guid]::NewGuid().ToString("N")
$password = "Sprint13-Test-Password!"
$employeeEmail = "employee-$suffix@example.com"
$reviewerEmail = "reviewer-$suffix@example.com"
$managerEmail = "manager-$suffix@example.com"
```

## 3. Register the users

Register an employee, reviewer, and manager. A successful registration returns `201 Created`.

```powershell
function Register-TestUser($email, $role, $employeeId) {
    $body = @{
        full_name = "Sprint 13 $role"
        email = $email
        role = $role
        employee_id = $employeeId
        department = "Engineering"
        designation = $role
        phone_number = "+1234567890"
        password = $password
    } | ConvertTo-Json

    Invoke-RestMethod -Uri "$baseUrl/users" -Method Post `
        -ContentType "application/json" -Body $body
}

$employee = Register-TestUser $employeeEmail "Employee" "EMP-$suffix"
$reviewer = Register-TestUser $reviewerEmail "Reviewer" "REV-$suffix"
$manager = Register-TestUser $managerEmail "Manager" "MGR-$suffix"
```

Save the returned IDs:

```powershell
$employeeId = $employee.id
$reviewerId = $reviewer.id
$managerId = $manager.id
```

Check that passwords are not present in any response.

## 4. Login and obtain JWT tokens

```powershell
function Login-TestUser($email) {
    $result = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method Post `
        -ContentType "application/x-www-form-urlencoded" `
        -Body @{ username = $email; password = $password }

    return $result.access_token
}

$employeeToken = Login-TestUser $employeeEmail
$reviewerToken = Login-TestUser $reviewerEmail
$managerToken = Login-TestUser $managerEmail
$employeeHeaders = @{ Authorization = "Bearer $employeeToken" }
$reviewerHeaders = @{ Authorization = "Bearer $reviewerToken" }
$managerHeaders = @{ Authorization = "Bearer $managerToken" }
```

Expected: `200 OK` and `token_type` equal to `bearer`.

Test invalid login:

```powershell
try {
    Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method Post `
        -ContentType "application/x-www-form-urlencoded" `
        -Body @{ username = $employeeEmail; password = "wrong-password" }
} catch { $_.Exception.Response.StatusCode.value__ }
```

Expected: `401 Unauthorized`.

## 5. Create a decision as the employee

```powershell
$decisionBody = @{
    title = "Select the production database"
    problem_statement = "The platform needs a reliable and scalable database."
    category = "Technology"
} | ConvertTo-Json

$decision = Invoke-RestMethod -Uri "$baseUrl/decisions" -Method Post `
    -Headers $employeeHeaders -ContentType "application/json" -Body $decisionBody

$decisionId = $decision.id
$decision.status
```

Expected: `201 Created`, `status` is `Draft`, and `created_by` equals `$employeeId`.

## 6. Add three alternatives

```powershell
function Add-Alternative($name, $cost, $feasibility, $risk) {
    $body = @{
        name = $name
        description = "Evaluate $name for the platform"
        pros = "Mature ecosystem and strong tooling"
        cons = "Requires operational ownership"
        estimated_cost = $cost
        feasibility_score = $feasibility
        risk_level = $risk
    } | ConvertTo-Json

    Invoke-RestMethod -Uri "$baseUrl/decisions/$decisionId/alternatives" `
        -Method Post -Headers $employeeHeaders `
        -ContentType "application/json" -Body $body
}

Add-Alternative "PostgreSQL" 10000 5 "Low"
Add-Alternative "MySQL" 8000 4 "Medium"
Add-Alternative "MongoDB" 12000 3 "High"
```

Expected: each request returns `201 Created` and the returned `decision_id` equals `$decisionId`.

Compare them:

```powershell
$comparison = Invoke-RestMethod -Uri `
    "$baseUrl/decisions/$decisionId/alternatives/compare" `
    -Headers $employeeHeaders
$comparison.alternatives.Count
```

Expected: `3`.

Validation check:

```powershell
$invalidAlternative = @{
    name = "Invalid option"
    description = "Invalid test"
    pros = "None"
    cons = "Invalid score"
    estimated_cost = 1
    feasibility_score = 6
    risk_level = "Low"
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "$baseUrl/decisions/$decisionId/alternatives" `
        -Method Post -Headers $employeeHeaders `
        -ContentType "application/json" -Body $invalidAlternative
} catch { $_.Exception.Response.StatusCode.value__ }
```

Expected: `422 Unprocessable Entity`.

## 7. Add discussion records

Comment:

```powershell
$comment = @{ content = "PostgreSQL has the strongest fit for our relational workload." } | ConvertTo-Json
Invoke-RestMethod -Uri "$baseUrl/decisions/$decisionId/comments" -Method Post `
    -Headers $employeeHeaders -ContentType "application/json" -Body $comment
```

Thread:

```powershell
$thread = @{
    title = "Database scalability"
    description = "Review expected growth and operational requirements."
} | ConvertTo-Json
$createdThread = Invoke-RestMethod -Uri "$baseUrl/decisions/$decisionId/threads" `
    -Method Post -Headers $employeeHeaders `
    -ContentType "application/json" -Body $thread
$threadId = $createdThread.id
```

Reply:

```powershell
$reply = @{ content = "The selected database must support read replicas." } | ConvertTo-Json
Invoke-RestMethod -Uri "$baseUrl/threads/$threadId/comments" -Method Post `
    -Headers $employeeHeaders -ContentType "application/json" -Body $reply
```

Rationale:

```powershell
$rationale = @{ rationale = "PostgreSQL balances reliability, feasibility, cost, and risk." } | ConvertTo-Json
Invoke-RestMethod -Uri "$baseUrl/decisions/$decisionId/rationale" -Method Put `
    -Headers $employeeHeaders -ContentType "application/json" -Body $rationale
```

## 8. Submit the decision for review

```powershell
$statusBody = @{ status = "Under Review" } | ConvertTo-Json
$submitted = Invoke-RestMethod -Uri "$baseUrl/decisions/$decisionId/status" `
    -Method Patch -Headers $employeeHeaders `
    -ContentType "application/json" -Body $statusBody
$submitted.status
```

Expected: `200 OK` and `Under Review`.

An invalid transition must fail:

```powershell
$invalidStatus = @{ status = "Approved" } | ConvertTo-Json
try {
    Invoke-RestMethod -Uri "$baseUrl/decisions/$decisionId/status" `
        -Method Patch -Headers $employeeHeaders `
        -ContentType "application/json" -Body $invalidStatus
} catch { $_.Exception.Response.StatusCode.value__ }
```

Expected: `409 Conflict`. The decision must be approved through the approval workflow.

## 9. Assign and complete approval

A manager assigns the reviewer:

```powershell
$assignment = @{ reviewer_id = $reviewerId } | ConvertTo-Json
$approval = Invoke-RestMethod -Uri "$baseUrl/decisions/$decisionId/approvals" `
    -Method Post -Headers $managerHeaders `
    -ContentType "application/json" -Body $assignment
$approvalId = $approval.id
```

The reviewer checks pending approvals:

```powershell
Invoke-RestMethod -Uri "$baseUrl/approvals/pending" -Headers $reviewerHeaders
```

The reviewer approves:

```powershell
$approvalAction = @{ status = "Approved"; comments = "Reviewed the alternatives and rationale." } | ConvertTo-Json
$completed = Invoke-RestMethod -Uri "$baseUrl/approvals/$approvalId" `
    -Method Patch -Headers $reviewerHeaders `
    -ContentType "application/json" -Body $approvalAction
$completed.status
```

Expected: `200 OK`, approval status `Approved`, and the decision status becomes `Approved`.

## 10. Verify authorization and authentication failures

No token:

```powershell
try { Invoke-RestMethod -Uri "$baseUrl/decisions/$decisionId" } catch { $_.Exception.Response.StatusCode.value__ }
```

Expected: `401 Unauthorized`.

Another employee attempting to update the decision must receive `403 Forbidden`. Create a second employee, login, then run:

```powershell
$otherHeaders = @{ Authorization = "Bearer $otherEmployeeToken" }
$update = @{ title = "Unauthorized title change" } | ConvertTo-Json
try {
    Invoke-RestMethod -Uri "$baseUrl/decisions/$decisionId" -Method Put `
        -Headers $otherHeaders -ContentType "application/json" -Body $update
} catch { $_.Exception.Response.StatusCode.value__ }
```

Expected: `403 Forbidden`.

## 11. Verify filters, timeline, audit, and versions

```powershell
Invoke-RestMethod -Uri "$baseUrl/decisions?status=Approved&category=Technology" `
    -Headers $employeeHeaders

Invoke-RestMethod -Uri "$baseUrl/decisions/search?q=database&status=Approved" `
    -Headers $employeeHeaders

Invoke-RestMethod -Uri "$baseUrl/decisions/$decisionId/timeline" `
    -Headers $employeeHeaders

Invoke-RestMethod -Uri "$baseUrl/decisions/$decisionId/history" `
    -Headers $employeeHeaders

Invoke-RestMethod -Uri "$baseUrl/decisions/$decisionId/versions" `
    -Headers $employeeHeaders
```

Confirm that the records reference the correct decision and user, and that no password or token appears in audit data.

## 12. Check dashboards and reports

Open Swagger and call the implemented dashboard and report endpoints with the employee, manager, or administrator token required by each route. Compare returned counts with the database:

- Employee dashboard: the employee's decisions and activities
- Manager dashboard: team decisions and pending approvals
- Administrator dashboard: organization-wide statistics
- Decision, approval, team, and audit reports
- PDF and Excel export endpoints, where implemented

Verify response codes, filters, totals, file content type, and exported row counts.

## 13. Final checklist

- `201` for successful user, decision, alternative, discussion, and approval creation
- `200` for successful reads, updates, login, and approval action
- `401` without a token or with invalid credentials
- `403` for a user changing another user's decision
- `404` for a missing decision, alternative, comment, thread, or approval
- `409` for invalid state transitions or repeated approval actions
- `422` for missing fields, invalid enum values, invalid risk levels, or feasibility outside `1` to `5`
- Decision status sequence: `Draft -> Under Review -> Approved`
- Audit and version records exist for decision changes
- No credentials or passwords appear in responses or logs
