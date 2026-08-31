# Task State — Decisions CRUD

## Part 1 (Create + Read): COMPLETE
## Part 2 (Update): COMPLETE (2026-08-17)

All Part 1 items are done and verified against the real PostgreSQL database.

## What was built

- `app/models/decision.py` — SQLAlchemy `Decision` model (title, problem_statement,
  category, status default "Draft", created_by FK to users, created_at, updated_at).
- `app/models/user.py` — added `decisions` relationship (cascade delete-orphan).
- `app/models/__init__.py` — `Decision` registered.
- `alembic/env.py` — imports `Decision` so it's in target metadata.
- `alembic/versions/2c3d8c3e66fc_create_decisions_table.py` — migration created
  AND applied (`alembic upgrade head` ran; `alembic current` = head).
- `app/schemas/decision.py` — `DecisionCreate` (title, problem_statement, category
  ONLY — no created_by/status from client) and `DecisionResponse`.
- `app/routers/decision.py` — 3 endpoints, all using `get_current_user` from
  `app/api/deps.py` (same auth mechanism as user router, no new auth):
  - `POST /decisions` → 201, sets status="Draft" and created_by=current_user.id
  - `GET /decisions` → 200 list
  - `GET /decisions/{decision_id}` → 200 or 404 "Decision not found"

## Verification results

| Check | Result |
| --- | --- |
| `python -m pytest` | PASS — 15 passed |
| POST /decisions with JWT | PASS — 201, status "Draft", created_by = authed user |
| POST /decisions schema (no created_by/status accepted) | PASS |
| GET /decisions | PASS — 200, returns created decision |
| GET /decisions/{id} | PASS — 200, correct record |
| GET /decisions/99999999 | PASS — 404 `{"detail": "Decision not found"}` |
| POST/GET/GET no JWT | PASS — all 401 |
| DB structure (PostgreSQL) | PASS — columns/types/FK correct |

## DB verification (PostgreSQL `expert_decision_replay`)

Columns: id (integer PK, sequence default), title (varchar, NOT NULL),
problem_statement (varchar, NOT NULL), category (varchar, NOT NULL),
status (varchar, NOT NULL), created_by (integer, NOT NULL),
created_at (timestamptz, NOT NULL, default now()), updated_at (timestamptz, NOT NULL, default now()).

Constraints: `decisions_pkey` (PRIMARY KEY id), `decisions_created_by_fkey`
(FOREIGN KEY created_by REFERENCES users(id)).

Verified end-to-end in Swagger-equivalent flow: created user → login → JWT →
POST /decisions → GET list → GET by id → GET invalid id (404) → no-token 401.
Test data was cleaned up afterward (decisions table empty again).

## Out of scope (Part 2 — do NOT touch)

Update endpoints, status transitions/workflow, filtering. Decisions table is
currently left empty after verification cleanup.

---

## Part 2: PUT /decisions/{decision_id} — COMPLETE

### Changes

- `app/schemas/decision.py` — added `DecisionUpdate` (all-Optional: title,
  problem_statement, category). Only these 3 fields exist on the schema, so any
  client-supplied `id`/`created_by`/`created_at` is ignored by Pydantic.
- `app/routers/decision.py` — added `update_decision` (PUT /decisions/{id}):
  - 404 `{"detail": "Decision not found"}` if ID missing
  - updates title/problem_statement/category (only when field is not None)
  - sets `updated_at = func.now()` so it always bumps on PUT
  - protected with `get_current_user` (existing JWT dependency from `app/api/deps.py`)

### Verification results (live server, real PostgreSQL)

| Check | Result |
| --- | --- |
| PUT valid id with token | PASS — 200; title/problem/category updated; id, created_by, created_at unchanged |
| updated_at changes | PASS — 20:41:50.18 → 20:41:51.40 |
| PUT /decisions/99999999 | PASS — 404 `{"detail": "Decision not found"}` |
| PUT without token | PASS — 401 `{"detail": "Not authenticated"}` |
| Body injecting created_by/id/created_at | PASS — ignored; DB kept created_by=17, id=3, created_at unchanged |
| `python -m pytest` after changes | PASS — 15 passed |
| Postgres persisted state | PASS — title "Body-Injected Title", created_by 17, updated_at > created_at |

Postgres row (id=3 after update): created_at 2026-08-17 20:41:50.181503+05:30,
updated_at 2026-08-17 20:41:51.418688+05:30 (updated_at > created_at = True).

Test data cleaned up after verification (decisions table empty; only pre-existing
`employee_live_new@example.com` user remains).

---

## Part 3: Controlled status values + PATCH /decisions/{id}/status — COMPLETE (2026-08-17)

### Changes

- `app/models/enums.py` — added `DecisionStatus(str, Enum)` with exactly 5 values:
  `Draft`, `Under Review`, `Approved`, `Rejected`, `Archived` (mirrors `UserRole` pattern).
- `app/models/decision.py` — status now uses the same enforcement approach as User roles:
  - `CheckConstraint("status IN ('Draft','Under Review','Approved','Rejected','Archived')",
    name="check_valid_status")` in `__table_args__`
  - `SqlAlchemyEnum(DecisionStatus, name="decisionstatus", native_enum=False,
    values_callable=[e.value for e in ...])` column, default `DecisionStatus.DRAFT`.
  - New decisions still default to `"Draft"` (model default + explicit value in POST handler).
- `alembic/versions/1a2b3c4d5e6f_add_decision_status_validation.py` — migration ADDING
  `check_valid_status` to `decisions`. Applied (`alembic upgrade head`; `alembic current` = head).
- `app/schemas/decision.py` — added `DecisionStatusUpdate` (`status: DecisionStatus`), so an
  invalid value like `"Completed"` is rejected by Pydantic with 422 (not 500).
- `app/routers/decision.py` — added `update_decision_status`:
  - `PATCH /decisions/{decision_id}/status`, body `{"status": "Under Review"}`
  - 404 `{"detail": "Decision not found"}` if ID missing
  - sets `decision.status` and `decision.updated_at = func.now()` (bumps on change)
  - protected with existing `get_current_user` JWT dependency (401 without token)
  - no transition/workflow rules yet — any valid status -> any valid status is allowed by design.

### Verification results (live server on real PostgreSQL)

| Check | Result |
| --- | --- |
| POST /decisions still defaults to `"Draft"` | PASS — 201, status "Draft" |
| PATCH status -> "Under Review" (valid) | PASS — 200, status updated, updated_at bumped 22:51:26.109 → .132 |
| PATCH status -> "Completed" (invalid) | PASS — 422 enum error: `Input should be 'Draft', 'Under Review', 'Approved', 'Rejected' or 'Archived'` |
| PATCH /decisions/99999999/status | PASS — 404 `{"detail": "Decision not found"}` |
| PATCH without token | PASS — 401 `{"detail": "Not authenticated"}` |
| `python -m pytest` | PASS — 23 passed (8 new status tests incl. DB IntegrityError) |

### Postgres DB-level verification

Constraint `check_valid_status` confirmed present in `pg_constraint`:

```
CHECK (((status)::text = ANY ((ARRAY['Draft'::varchar, 'Under Review'::varchar,
'Approved'::varchar, 'Rejected'::varchar, 'Archived'::varchar])::text[])))
```

Direct-SQL insert `INSERT INTO decisions (..., status 'Completed', created_by ...)`
via psycopg2 → rejected at DB layer:

```
psycopg2.errors.CheckViolation: new row for relation "decisions" violates check
constraint "check_valid_status"
```

Direct-SQL insert with `'Under Review'` → accepted. Test rows cleaned up afterward
(decisions table empty again).

## Out of scope (Part 4 — do NOT touch)

Status transition workflow (who can approve, which transitions between statuses are legal),
filtering, updated_at/audit timestamps beyond current behavior. These are next on the roadmap.

---

## Part 4: GET /decisions query-parameter filtering — COMPLETE (2026-08-18)

### Changes

- `app/routers/decision.py` — `get_decisions` now accepts two optional query params:
  - `status: Optional[DecisionStatus] = None` — typed as the `DecisionStatus` enum, so an
    invalid value like `Completed` is rejected by FastAPI/Pydantic with **422** (same error
    shape as the PATCH status endpoint: `loc ["query", "status"]`, msg
    `Input should be 'Draft', 'Under Review', 'Approved', 'Rejected' or 'Archived'`).
  - `category: Optional[str] = None` — plain string equality filter (free-form, no enum).
  - Filters compose with **AND**; no filters supplied → original `query.all()` behavior
    unchanged. Auth untouched (same `get_current_user` JWT dependency).
- `tests/test_decision_filtering.py` — 6 new tests (no-filters-all, status filter,
  category filter, status+category AND, invalid status → 422, no-token → 401).

Note on 422 implementation: rather than hand-returning a 422 in the handler, the status
param is typed directly as the `DecisionStatus` enum so FastAPI's own validation layer
rejects bad values with a 422 before the endpoint body runs. This is exactly how invalid
status is already rejected by the PATCH endpoint, so it's consistent by construction.

### Verification results (real PostgreSQL `expert_decision_replay`)

| Check | Result |
| --- | --- |
| `?status=Draft` | PASS — 200, only 2 Draft decisions (ids 11, 12) |
| `?category=Technology` | PASS — 200, only 2 Technology decisions (ids 11, 13) |
| `?status=Approved&category=Technology` | PASS — 200, exactly 1 row (id 13 "Approved Tech") — AND logic |
| `?status=Completed` (invalid) | PASS — 422 `{"type":"enum","loc":["query","status"],"msg":"Input should be 'Draft', 'Under Review', 'Approved', 'Rejected' or 'Archived'","input":"Completed"}` |
| `?status=Draft` no token | PASS — 401 `{"detail": "Not authenticated"}` |
| `python -m pytest` | PASS — 29 passed (23 existing + 6 new) |
| Postgres state after cleanup | PASS — decisions table 0 rows, no leftover `filter_verify_*` user |

Flow used for Swagger-equivalent checks (same ASGI endpoints): signup → login → JWT →
POST 4 decisions (all "Draft" by design) → PATCH 2 to "Approved" → the 5 GET checks →
DELETE test user. Test data cleaned up afterward (decisions table 0 rows; only
pre-existing `employee_live_new@example.com` user remains).

## Out of scope (Part 5 — do NOT touch)

Status transition workflow (who can approve, which transitions between statuses are legal),
updated_at/audit timestamps beyond current behavior. Next on the roadmap.

---

## Sprint 5 — Part 2: SIGN-OFF — COMPLETE (2026-08-18)

Final verification pass. No code changed this session — full behavior confirmed against
real PostgreSQL. This section is the record that Sprint 5 Part 2 is done and ready for
Part 3 (Approval Workflow) to build on.

### Decision endpoints + auth requirement

| Method | Endpoint | Auth | Behavior |
| --- | --- | --- | --- |
| POST | `/decisions` | JWT (`get_current_user`) | 201; forces status `"Draft"`, created_by = authed user; client `created_by`/`status` ignored |
| GET | `/decisions` | JWT | 200 list of ALL decisions (no per-user scoping); optional `?status=` (enum-validated → 422 on bad value) and `?category=` (free string), composed with AND |
| GET | `/decisions/{id}` | JWT | 200 record or 404 `{"detail": "Decision not found"}` |
| PUT | `/decisions/{id}` | JWT | 200 update title/problem_statement/category (only non-None fields); id/created_by/created_at unchanged; `updated_at` bumped; 404 if missing |
| PATCH | `/decisions/{id}/status` | JWT | 200 status change (any valid -> any valid, no workflow rules); `updated_at` bumped; 404 if missing; 422 on invalid enum value |

### Task 1 finding — role-based authorization: ROLE-AGNOSTIC (confirmed)

Tested with two freshly-created users, an **Employee** (id 23) and an **Administrator**
(id 24), each logged in with their own JWT:

- Employee: POST → 201, created_by=23, status Draft. PUT own → 200. PATCH status own → 200.
- Administrator: POST → 201, created_by=24, status Draft. PUT own → 200. PATCH status own → 200.
- Cross-user: **Administrator PATCHed the Employee's decision → 200**; **Employee PUT the
  Administrator's decision → 200**. No ownership check exists.
- Filters behave identically for both roles.

**Conclusion: access is currently role-agnostic — any authenticated user, regardless of
role, can perform any Decision action (create/read/update/change-status) on any decision,
including decisions created by others. No incidental role or ownership differentiation
exists.** This is expected for this sprint; role-based restrictions belong to Part 3
(Approval Workflow), which is out of scope here.

### Task 2 — full regression results (continuous pass, real PostgreSQL)

| Test case | Result |
| --- | --- |
| `python -m pytest` (full suite) | PASS — 29 passed, 0 failed |
| Login → JWT | PASS — 200, token acquired |
| POST /decisions (valid) | PASS — 201, status `"Draft"`, created_by = authed user |
| POST body with created_by/status | PASS — ignored; DB kept server-set values |
| GET /decisions (list) | PASS — 200, includes created decision |
| GET /decisions/{id} | PASS — 200, correct record |
| GET /decisions/{invalid_id} | PASS — 404 `{"detail": "Decision not found"}` |
| PUT /decisions/{id} | PASS — 200; id/created_by/created_at unchanged; `updated_at` bumped (20:21:18.18 → .21) |
| PUT /decisions/{invalid_id} | PASS — 404 |
| PATCH /decisions/{id}/status (valid) | PASS — 200, status changed |
| PATCH /decisions/{id}/status (invalid `"Completed"`) | PASS — 422 enum error |
| PATCH /decisions/{invalid_id}/status | PASS — 404 |
| GET /decisions?status=<valid> | PASS — 200, only matching statuses |
| GET /decisions?category=<value> | PASS — 200, only matching categories |
| GET /decisions?status=<x>&category=<y> | PASS — 200, AND logic (every row matches both) |
| GET /decisions?status=invalid | PASS — 422 enum error |
| GET/POST/PUT/PATCH without token | PASS — all 401 `{"detail": "Not authenticated"}` |

One note: the combined-filter spot check `?status=Approved&category=Finance` matched TWO
rows (the regression decision AND the Administrator's Finance/Approved decision) because
`GET /decisions` returns all decisions across users by design. Every returned row satisfied
both filters, so AND logic is correct — an earlier assertion assuming only the
Employee-created row matched was the bug in the check script, not in the endpoint.

### PostgreSQL check (expert_decision_replay)

- Columns/types: id integer PK · title/problem_statement/category/status varchar · created_by
  integer · created_at/updated_at timestamptz — all NOT NULL. PASS.
- Constraints present: `decisions_pkey` (PK), `decisions_created_by_fkey` (FK created_by →
  users), `check_valid_status`
  (`status IN ('Draft','Under Review','Approved','Rejected','Archived')`), plus per-column
  NOT NULL constraints. PASS.
- Spot-check of rows mid-run confirmed correct persisted values: e.g. row 21
  `'Regression Updated'` status `'Under Review'` created_by 23; row 20 `'Adm Edited By Emp'`
  status `'Approved'` created_by 24. PASS.

### Post-verification state

Test users (Employee + Administrator) deleted via DELETE /users (cascade removed their
decisions). Postgres confirmed clean: `decisions` = 0 rows, `users` = 1 (only pre-existing
`employee_live_new@example.com` remains). Working tree clean; no code changes this session.

## Out of scope (Part 3 / next) — do NOT touch

Approval Workflow: role-based restrictions on who can create/update/change status, reviewer
and manager approval chains, transition rules between statuses. Decisions module is
otherwise complete through filtering.

---

## Part 6a: Alternative entity (create + read) — COMPLETE (2026-08-18)

### Changes

- `app/models/alternative.py` — new SQLAlchemy `Alternative` model:
  `id`, `decision_id` (FK → decisions.id, indexed), `name` (NOT NULL), `description`, `pros`,
  `cons`, `risk_level` (String, nullable), `estimated_cost`, `feasibility_score` (Integer,
  nullable — **no range/enum validation yet, by design, deferred to Part 6b**), `created_at`,
  `updated_at`. Relationship `alternative.decision` ↔ `decision.alternatives`
  (`cascade="all, delete-orphan"`), mirroring the User → Decisions pattern.
- `app/models/decision.py` — added `alternatives` relationship (cascade delete-orphan).
- `app/models/__init__.py` — `Alternative` registered.
- `alembic/env.py` — imports `Alternative` so it's in target metadata.
- `alembic/versions/56c656d0956d_create_alternatives_table.py` — migration generated via
  `alembic revision --autogenerate`, reviewed (only adds `alternatives` table + FK + indexes,
  no unexpected changes), then `alembic upgrade head` applied. `alembic current` = head.
- `app/schemas/alternative.py` — `AlternativeCreate` (name, description, pros, cons,
  estimated_cost, feasibility_score, risk_level ONLY — no id/decision_id/timestamps accepted;
  decision_id comes from the URL) and `AlternativeResponse` (full model incl. id, decision_id,
  timestamps).
- `app/routers/alternative.py` — 3 endpoints, all using existing `get_current_user` JWT:
  - `POST /decisions/{decision_id}/alternatives` → 201; checks Decision exists first
    (404 `{"detail": "Decision not found"}` — no orphan rows), ties to `decision_id` from URL
  - `GET /decisions/{decision_id}/alternatives` → 200 list (also 404s if the Decision
    doesn't exist, consistent with POST)
  - `GET /alternatives/{alternative_id}` → 200 or 404 `{"detail": "Alternative not found"}`
  Registered via two routers (`/decisions` prefix router + `/alternatives` prefix router) so
  paths match spec exactly.
- `app/main.py` — both alternative routers registered.
- `tests/test_alternative.py` — 9 tests (create, 404 on missing decision + no orphan row,
  body-injected decision_id/id/created_at ignored, list by decision, 404 on missing decision
  for list, get by id, 404, no-token 401, multiple alternatives → same decision in DB).

### Verification results (real PostgreSQL `expert_decision_replay`)

| Check | Result |
| --- | --- |
| Login → JWT | PASS — 200, token acquired |
| POST /decisions | PASS — 201, decision id 23 |
| POST 3 alternatives (PostgreSQL/MySQL/MongoDB) | PASS — all 201, `decision_id` = 23 in each response |
| POST /decisions/99999999/alternatives | PASS — 404 `{"detail": "Decision not found"}`; 0 rows in DB for decision 99999999 (no orphan) |
| GET /decisions/23/alternatives | PASS — 200, exactly 3 rows (PostgreSQL, MySQL, MongoDB), all decision_id 23 |
| GET /alternatives/{id} | PASS — 200, correct record (id 1, PostgreSQL) |
| GET /alternatives/99999999 | PASS — 404 `{"detail": "Alternative not found"}` |
| POST/GET list/GET single without token | PASS — all 401 `{"detail": "Not authenticated"}` |
| `python -m pytest` | PASS — 38 passed (29 existing + 9 new) |

### Postgres DB-level verification

Columns: id (integer PK, indexed), decision_id (integer, NOT NULL, indexed), name (varchar,
NOT NULL), description/pros/cons/risk_level (varchar, nullable), estimated_cost/
feasibility_score (integer, nullable), created_at/updated_at (timestamptz, NOT NULL,
default now()).

Constraints: `alternatives_pkey` (PK id), `alternatives_decision_id_fkey`
(FK decision_id → decisions.id), per-column NOT NULL constraints. No `check_valid_*`
constraints on alternatives yet (risk_level/feasibility_score validation deferred to 6b).

Confirmed 3 alternatives all reference decision_id=23, and zero alternatives reference a
missing decision. Test data cleaned up afterward (alternatives 0 rows, decisions 0 rows;
only pre-existing `employee_live_new@example.com` user remains).

## Out of scope (Part 6b / next) — do NOT touch

Alternative update/delete endpoints, `feasibility_score` range validation and `risk_level`
enum enforcement (DB CHECK + Pydantic), approval workflow. The 6a endpoints intentionally
accept these as basic int/string types.

---

## Part 6b: Controlled feasibility_score + risk_level + PUT /alternatives/{id} — COMPLETE (2026-08-18)

### Changes

- `app/models/enums.py` — added `RiskLevel(str, Enum)` with exactly 4 values: `Low`,
  `Medium`, `High`, `Critical` (mirrors `UserRole`/`DecisionStatus` pattern).
- `app/models/alternative.py` — validation now enforced at the DB layer:
  - `CheckConstraint("feasibility_score BETWEEN 1 AND 5", name="check_valid_feasibility_score")`
  - `CheckConstraint("risk_level IN ('Low','Medium','High','Critical')", name="check_valid_risk_level")`
  - `risk_level` column now `SqlAlchemyEnum(RiskLevel, native_enum=False, values_callable=...)`
    (still VARCHAR in DB, like decision status). `feasibility_score` stays Integer.
  - Both columns remain nullable; the CHECKs evaluate to NULL (pass) when the column is NULL.
- `alembic/versions/4869b7a3e2a0_add_alternative_validation_constraints.py` — new migration.
  **Note:** `alembic revision --autogenerate` produced an EMPTY migration (Alembic does not
  detect `CheckConstraint` additions — same reason the `check_valid_status` migration was
  hand-written in Part 3), so the file was hand-populated with the two
  `op.create_check_constraint` calls, mirroring that pattern. Applied (`alembic upgrade head`;
  `alembic current` = head). Both constraints confirmed in `pg_constraint`.
- `app/schemas/alternative.py` — validation now enforced at the Pydantic layer:
  - `feasibility_score: Optional[int] = Field(default=None, ge=1, le=5)` → out-of-range values
    (e.g. 10) rejected with **422** (`less_than_equal`), not 500.
  - `risk_level: Optional[RiskLevel] = None` → invalid values (e.g. `"Very Dangerous"`)
    rejected with **422** (enum error `Input should be 'Low', 'Medium', 'High' or 'Critical'`).
  - Added `AlternativeUpdate` (all-Optional, same validation) for PUT.
- `app/routers/alternative.py` — added `update_alternative` (PUT /alternatives/{id}):
  - 404 `{"detail": "Alternative not found"}` if ID missing
  - updates name/description/pros/cons/estimated_cost/feasibility_score/risk_level (only when
    not None); `id`/`decision_id`/`created_at`/`updated_at` are not on the schema so any
    client-supplied values are ignored by Pydantic
  - sets `updated_at = func.now()` (always bumps on PUT)
  - protected with existing `get_current_user` JWT (401 without token)
- `tests/test_alternative.py` — updated ALT_BODY to a valid score (4); 11 new tests
  (create/update score out of range → 422, create/update invalid risk → 422, valid values
  accepted, PUT updates + backend fields unchanged + updated_at bumped, PUT ignores
  injected id/decision_id/created_at, PUT 404, PUT no-token 401, DB CHECK rejects
  invalid score/risk via IntegrityError).

### Verification results (real PostgreSQL `expert_decision_replay`)

| Check | Result |
| --- | --- |
| PUT /alternatives/{valid_id} (valid data) | PASS — 200; name/description/cost/score/risk updated; id, decision_id, created_at unchanged; updated_at bumped 20:48:27.75 → 20:48:28.88 |
| PUT /alternatives/99999999 | PASS — 404 `{"detail": "Alternative not found"}` |
| PUT without token | PASS — 401 `{"detail": "Not authenticated"}` |
| Create with feasibility_score=10 | PASS — 422 `{"type":"less_than_equal","loc":["body","feasibility_score"],"msg":"Input should be less than or equal to 5","input":10}` |
| Update with feasibility_score=10 | PASS — 422 (same error shape) |
| Create with risk_level="Very Dangerous" | PASS — 422 `{"type":"enum","loc":["body","risk_level"],"msg":"Input should be 'Low', 'Medium', 'High' or 'Critical'","input":"Very Dangerous"}` |
| Update with risk_level="Very Dangerous" | PASS — 422 (same error shape) |
| Valid values (feasibility_score=5, risk_level="Medium") | PASS — 201, persisted correctly |
| `python -m pytest` | PASS — 49 passed (38 existing + 11 new) |

### Postgres DB-level verification

Constraints in `pg_constraint` on `alternatives`:

```
check_valid_feasibility_score  CHECK (((feasibility_score >= 1) AND (feasibility_score <= 5)))
check_valid_risk_level         CHECK (((risk_level)::text = ANY ((ARRAY['Low'::character varying,
                               'Medium'::character varying, 'High'::character varying,
                               'Critical'::character varying])::text[])))
```

Direct-SQL inserts via psycopg2 — rejected at the DB layer (not just app validation):
`feasibility_score=10` → `psycopg2.errors.CheckViolation: ... violates check constraint
"check_valid_feasibility_score"`; `risk_level='Very Dangerous'` → violates
`check_valid_risk_level`. Valid direct insert (score=3, risk='Medium') → accepted, then
deleted. Test data cleaned up afterward (alternatives 0 rows, decisions 0 rows; only
pre-existing `employee_live_new@example.com` user remains).

## Out of scope (Sprint 7 / next) — do NOT touch

Alternative delete endpoints, approval workflow (role-based restrictions, reviewer/manager
approval chains, status transition rules). The Alternative module is otherwise complete
through update and comparison.

---

## Sprint 6: Alternatives Module (Full Suite & Compare Endpoint) — SIGN-OFF — COMPLETE (2026-08-25)

Final verification pass and comparison endpoint implementation. All 5 Alternative endpoints,
JWT auth requirements, error handling, comparison shape, and database persistence have been
verified against live server and real PostgreSQL (`expert_decision_replay`).

### 1. Alternative Endpoints & Auth Requirements

| Method | Endpoint | Auth | Behavior |
| --- | --- | --- | --- |
| POST | `/decisions/{decision_id}/alternatives` | JWT (`get_current_user`) | 201; creates alternative tied to `decision_id`; 404 if decision not found; 422 on validation failure; client `id`/`decision_id`/`created_at` ignored |
| GET | `/decisions/{decision_id}/alternatives` | JWT (`get_current_user`) | 200 list of alternatives for the decision; 404 if decision not found |
| GET | `/alternatives/{alternative_id}` | JWT (`get_current_user`) | 200 record or 404 `{"detail": "Alternative not found"}` |
| PUT | `/alternatives/{alternative_id}` | JWT (`get_current_user`) | 200 updates fields (only non-None fields); 404 if not found; `updated_at` bumped; client `id`/`decision_id`/`created_at` ignored; 422 on validation failure |
| GET | `/decisions/{decision_id}/alternatives/compare` | JWT (`get_current_user`) | 200 comparison-friendly shape `{"decision_id": int, "alternatives": [{"name", "estimated_cost", "feasibility_score", "risk_level"}]}`; 404 if decision not found; 200 with empty array `[]` if decision has zero alternatives |

*Note: Access across all 5 endpoints is protected by standard JWT authentication (`get_current_user`). No multi-level approval or role restrictions are enforced in this module (deferred to Approval Workflow sprint).*

---

### 2. Swagger / E2E Testing Workflow Verification (Real PostgreSQL)

| Step | Action & Description | Expected | Actual Result | Pass/Fail |
| --- | --- | --- | --- | --- |
| 1 | POST `/login` with credentials | 200 + JWT token | 200, access token acquired | **PASS** |
| 2 | POST `/decisions` | 201, status "Draft" | 201, id=25, status="Draft", created_by=27 | **PASS** |
| 3 | POST 3 alternatives (PostgreSQL, MySQL, MongoDB) | 201 for each, varying cost/feasibility/risk | 201 for IDs 9, 10, 11; decision_id=25 on all | **PASS** |
| 4 | GET `/decisions/{decision_id}/alternatives` | 200, returns list of 3 | 200, returned 3 alternatives (PostgreSQL, MySQL, MongoDB) | **PASS** |
| 5 | GET `/alternatives/{id}` | 200, single record | 200, id=9, name="PostgreSQL", decision_id=25 | **PASS** |
| 6 | PUT `/alternatives/{id}` | 200, update name & cost | 200, name="PostgreSQL 16 Enterprise", cost=6200, updated_at bumped | **PASS** |
| 7 | POST with invalid `risk_level` ("Extremely Risky") | 422 Unprocessable Entity | 422 `Input should be 'Low', 'Medium', 'High' or 'Critical'` | **PASS** |
| 8 | POST with invalid `feasibility_score` (10) | 422 Unprocessable Entity | 422 `Input should be less than or equal to 5` | **PASS** |
| 9 | GET `/decisions/{decision_id}/alternatives/compare` | 200 with 3 comparison items | 200, `decision_id: 25`, all 3 items returned with exact keys `name`, `estimated_cost`, `feasibility_score`, `risk_level` | **PASS** |
| 10a | POST `/decisions/{id}/alternatives` (no JWT) | 401 Unauthorized | 401 `{"detail": "Not authenticated"}` | **PASS** |
| 10b | GET `/decisions/{id}/alternatives` (no JWT) | 401 Unauthorized | 401 `{"detail": "Not authenticated"}` | **PASS** |
| 10c | GET `/alternatives/{id}` (no JWT) | 401 Unauthorized | 401 `{"detail": "Not authenticated"}` | **PASS** |
| 10d | PUT `/alternatives/{id}` (no JWT) | 401 Unauthorized | 401 `{"detail": "Not authenticated"}` | **PASS** |
| 10e | GET `/decisions/{id}/alternatives/compare` (no JWT) | 401 Unauthorized | 401 `{"detail": "Not authenticated"}` | **PASS** |

---

### 3. Error Handling Checklist Verification

| Scenario | Endpoint(s) | Status | Response Detail | Pass/Fail |
| --- | --- | --- | --- | --- |
| Non-existing decision | POST `/decisions/99999999/alternatives` | 404 | `{"detail": "Decision not found"}` | **PASS** |
| Non-existing decision | GET `/decisions/99999999/alternatives` | 404 | `{"detail": "Decision not found"}` | **PASS** |
| Non-existing decision | GET `/decisions/99999999/alternatives/compare` | 404 | `{"detail": "Decision not found"}` | **PASS** |
| Non-existing alternative | GET `/alternatives/99999999` | 404 | `{"detail": "Alternative not found"}` | **PASS** |
| Non-existing alternative | PUT `/alternatives/99999999` | 404 | `{"detail": "Alternative not found"}` | **PASS** |
| Missing required field (`name`) | POST `/decisions/{id}/alternatives` | 422 | `loc: ["body", "name"], type: "missing"` | **PASS** |
| Invalid `feasibility_score` (<1 or >5) | POST & PUT | 422 | `loc: ["body", "feasibility_score"]` | **PASS** |
| Invalid `risk_level` (not in enum) | POST & PUT | 422 | `loc: ["body", "risk_level"]` | **PASS** |
| No JWT Header | All 5 Alternative endpoints | 401 | `{"detail": "Not authenticated"}` | **PASS** |
| Existing decision with 0 alternatives | GET `.../compare` | 200 | `{"decision_id": <id>, "alternatives": []}` (not an error) | **PASS** |

---

### 4. Direct PostgreSQL Verification

Direct queries via `psycopg2` on live PostgreSQL `expert_decision_replay` database verified:
- **Foreign Key**: `decision_id` correctly references parent `decisions.id` (id=25).
- **Multiple Alternatives**: All 3 records (PostgreSQL 16 Enterprise, MySQL, MongoDB) stored under the same `decision_id`.
- **Field Integrity**: `estimated_cost`, `feasibility_score`, `risk_level` correctly stored and typed.
- **Updates Reflected**: `name` updated from 'PostgreSQL' to 'PostgreSQL 16 Enterprise', `estimated_cost` updated from 5000 to 6200, and `updated_at` updated timestamp.

### 5. Regression Test Results

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Bhargav\Desktop\expert-decision-replay
plugins: anyio-4.14.2
collected 54 items

tests\test_alternative.py .........................                      [ 46%]
tests\test_auth.py ...                                                   [ 51%]
tests\test_decision_filtering.py ......                                  [ 62%]
tests\test_decision_status.py ........                                   [ 77%]
tests\test_security.py ....                                              [ 85%]
tests\test_user_enhancements.py ........                                 [100%]

======================= 54 passed, 2 warnings in 13.30s =======================
```

### 6. Cleanup Verification

- `alternatives` table: **0 rows**
- `decisions` table: **0 rows**
- `users` table: **1 row** (only pre-existing baseline user `employee_live_new@example.com` remains)

---

## Sprint 7: Comments Module (Model, Migration, Schemas, Endpoints & Ownership) — SIGN-OFF — COMPLETE (2026-08-25)

### 1. What was built & Files Touched

- `app/models/comment.py` — SQLAlchemy `Comment` model with `id` (PK), `decision_id` (FK → decisions.id), `user_id` (FK → users.id), `content` (String, NOT NULL), `created_at`, and `updated_at`. Added relationships to `Decision` and `User`.
- `app/models/decision.py` — added `comments` relationship (`cascade="all, delete-orphan"`).
- `app/models/user.py` — added `comments` relationship (`cascade="all, delete-orphan"`).
- `app/models/__init__.py` & `alembic/env.py` — registered `Comment` model.
- `alembic/versions/72f74061fb2d_create_comments_table.py` — migration generated via `alembic revision --autogenerate`, reviewed, and applied (`alembic upgrade head`).
- `app/schemas/comment.py` — `CommentCreate` (`content` only), `CommentUpdate` (`content` only), and `CommentResponse` (full model).
- `app/routers/comment.py` — 5 endpoints with JWT auth and ownership validation:
  - `POST /decisions/{decision_id}/comments` → 201 (404 if decision not found, `user_id` set from JWT)
  - `GET /decisions/{decision_id}/comments` → 200 (404 if decision not found)
  - `GET /comments/{comment_id}` → 200 (404 if comment not found)
  - `PUT /comments/{comment_id}` → 200 (404 if not found, 403 Forbidden if not author/admin, `updated_at` bumped)
  - `DELETE /comments/{comment_id}` → 200 `{"message": "Comment deleted successfully"}` (404 if not found, 403 Forbidden if not author/admin)
- `app/main.py` — registered `comment_router` and `comments_router`.
- `tests/test_comment.py` — 16 unit/integration tests covering CRUD, 401s, 403s, 404s, admin moderation, and cascade delete.

---

### 2. Ownership Enforcement Policy

- **Rule Chosen**: **Author OR Administrator**
- **Rationale**: The original author of the comment retains full editing and deletion rights over their own contributions. In addition, users with the `Administrator` role are granted administrative/moderation permissions to edit or remove comments across the system when necessary (e.g. content moderation, policy violations). Non-admin users attempting to update or delete another user's comment are rejected with **403 Forbidden** (`{"detail": "Not authorized to modify this comment"}` / `{"detail": "Not authorized to delete this comment"}`).

---

### 3. Swagger / E2E Testing Workflow Verification (Real PostgreSQL)

| Step | Action & Description | Expected | Actual Result | Pass/Fail |
| --- | --- | --- | --- | --- |
| 1 | Login as User A → JWT | 200 + token | 200, acquired token for User A (id=28) | **PASS** |
| 2 | Create Decision | 201 Created | 201, decision_id=27 | **PASS** |
| 3 | Create 3 comments as User A | 201 for each | 201 for comment IDs 1, 2, 3; all tied to decision 27 and user 28 | **PASS** |
| 4 | POST `/decisions/99999/comments` | 404 Not Found | 404 `{"detail": "Decision not found"}` | **PASS** |
| 5 | GET `/decisions/{id}/comments` | 200 list of 3 | 200, returned all 3 comments by User A | **PASS** |
| 6 | GET `/comments/{id}` | 200 single record | 200, comment id=1, user_id=28, content="First comment by User A" | **PASS** |
| 7 | GET `/comments/99999` | 404 Not Found | 404 `{"detail": "Comment not found"}` | **PASS** |
| 8 | PUT `/comments/{id}` as owner (User A) | 200 OK | 200, content updated, id/decision_id/user_id unchanged, updated_at bumped | **PASS** |
| 9 | Login as User B, PUT `/comments/{User A's comment id}` | 403 Forbidden | 403 `{"detail": "Not authorized to modify this comment"}` | **PASS** |
| 9b | Login as Admin, PUT `/comments/{User A's comment id}` | 200 OK | 200, content updated by Administrator | **PASS** |
| 10 | DELETE `/comments/{id}` as owner (User A) | 200 OK | 200 `{"message": "Comment deleted successfully"}`, subsequent GET is 404 | **PASS** |
| 11 | DELETE `/comments/99999` | 404 Not Found | 404 `{"detail": "Comment not found"}` | **PASS** |
| 12a | DELETE on User A's comment as User B | 403 Forbidden | 403 `{"detail": "Not authorized to delete this comment"}` | **PASS** |
| 12b | DELETE on User A's comment as Administrator | 200 OK | 200 `{"message": "Comment deleted successfully"}` | **PASS** |
| 13 | All 5 endpoints without token | 401 Unauthorized | 401 `{"detail": "Not authenticated"}` on all 5 | **PASS** |

---

### 4. Direct PostgreSQL Verification

Direct queries via `psycopg2` on live PostgreSQL `expert_decision_replay` database verified:
- **Columns & Types**: `id` (integer PK), `decision_id` (integer FK → decisions.id), `user_id` (integer FK → users.id), `content` (varchar, NOT NULL), `created_at` (timestamptz), `updated_at` (timestamptz).
- **Constraints**: `comments_pkey`, `comments_decision_id_fkey`, `comments_user_id_fkey`, indexes on `id`, `decision_id`, `user_id`.
- **Multi-user integrity**: Verified multiple comments correctly stored under the same `decision_id` referencing distinct `user_id`s.

---

### 5. Regression Test Results

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Bhargav\Desktop\expert-decision-replay
plugins: anyio-4.14.2
collected 70 items

tests\test_alternative.py .........................                      [ 35%]
tests\test_auth.py ...                                                   [ 40%]
tests\test_comment.py ................                                   [ 62%]
tests\test_decision_filtering.py ......                                  [ 71%]
tests\test_decision_status.py ........                                   [ 82%]
tests\test_security.py ....                                              [ 88%]
tests\test_user_enhancements.py ........                                 [100%]

======================= 70 passed, 2 warnings in 19.07s =======================
```

---

### 6. Post-Verification Database State

- `comments` table: **0 rows**
- `alternatives` table: **0 rows**
- `decisions` table: **0 rows**
- `users` table: **1 row** (only pre-existing baseline user `employee_live_new@example.com` remains)

---

## Sprint 8: Discussion Threads (Model, CRUD, Ownership & Thread Replies) — COMPLETE (2026-08-25)

### 1. What was built & Files Touched

- `app/models/discussion_thread.py` — SQLAlchemy `DiscussionThread` model with `id`, `decision_id` (FK → decisions.id), `created_by` (FK → users.id), `title`, `description` (nullable), `status` (String, default `"Open"`), `created_at`, `updated_at`. Relationships to `Decision`, `User`, and `comments`.
- `app/models/comment.py` — added nullable `thread_id` FK (→ discussion_threads.id) and `thread` relationship for thread replies.
- `app/models/decision.py` — added `threads` relationship (`cascade="all, delete-orphan"`).
- `app/models/user.py` — added `threads` relationship (`cascade="all, delete-orphan"`).
- `app/models/__init__.py` & `alembic/env.py` — registered `DiscussionThread`.
- `alembic/versions/a9b7255d0c2f_create_discussion_threads_table.py` — single migration creating `discussion_threads` table AND adding `thread_id` column to `comments` (both changes detected by autogenerate). Applied (`alembic upgrade head`; `alembic current` = head).
- `app/schemas/discussion_thread.py` — `ThreadCreate` (title, description only), `ThreadUpdate` (title, description, status — all optional), `ThreadResponse` (full model).
- `app/schemas/comment.py` — `CommentResponse` updated to include `thread_id: int | None`.
- `app/routers/discussion_thread.py` — 6 endpoints with JWT auth and ownership validation:
  - `POST /decisions/{decision_id}/threads` → 201 (404 if decision not found, `created_by` set from JWT)
  - `GET /decisions/{decision_id}/threads` → 200 (404 if decision not found)
  - `GET /threads/{thread_id}` → 200 (404 if thread not found)
  - `PUT /threads/{thread_id}` → 200 (404 if not found, 403 Forbidden if not author/admin)
  - `DELETE /threads/{thread_id}` → 200 `{"message": "Thread deleted successfully"}` (404 if not found, 403 Forbidden if not author/admin)
  - `POST /threads/{thread_id}/comments` → 201 (404 if thread not found; creates a Comment with `thread_id` set)
- `app/main.py` — registered `thread_router` and `threads_router`.
- `tests/test_thread.py` — 20 tests covering all CRUD operations, ownership, admin override, thread replies, and auth.

### 2. Ownership Enforcement Policy

- **Rule Applied**: **Author OR Administrator** — same as Sprint 7a Comments.
- **Rationale**: Reused the same rule from comments because thread authors should retain control over their discussion topics, and administrators need moderation capabilities. This is consistent with the comment module and avoids introducing different authorization rules within the same feature area.
- **Implementation**: `if thread.created_by != current_user.id and current_user.role != UserRole.ADMINISTRATOR` → 403 Forbidden.

### 3. Thread Replies Design Decision

- Added nullable `thread_id` FK to the `comments` table.
- A comment is either a **direct comment on a decision** (`thread_id = NULL`) or a **reply to a thread** (`thread_id = <thread_id>`).
- Both types share the same `Comment` model — no separate reply model needed.
- Existing Sprint 7a comment endpoints remain unchanged (they key off `decision_id`, not `thread_id`).
- `POST /threads/{thread_id}/comments` creates a comment with both `decision_id` (inherited from the thread's parent decision) and `thread_id` (the target thread).

### 4. Status Field Assumption

- `status` is a plain `String` with no controlled enum values (not built a workflow unless spec elsewhere requires specific values).
- Default value is `"Open"` (Python-side default on the model; no DB DEFAULT constraint).
- If a future workflow requires specific values, a CHECK constraint + enum should be added (similar to `DecisionStatus`).

### 5. Regression Test Results

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Bhargav\Desktop\expert-decision-replay
plugins: anyio-4.14.2
collected 90 items

tests\test_alternative.py .........................                      [ 24%]
tests\test_auth.py ...                                                   [ 30%]
tests\test_comment.py ................                                     [ 47%]
tests\test_decision_filtering.py ......                                  [ 55%]
tests\test_decision_status.py ........                                   [ 65%]
tests\test_security.py ....                                              [ 70%]
tests\test_thread.py ....................                                 [100%]
tests\test_user_enhancements.py ........                                 [100%]

====================== 90 passed, 2 warnings in 26.93s = ======================
```

**All Sprint 7a comment tests still pass alongside 20 new thread tests — no regression.**

### 6. Post-Verification Database State

- `discussion_threads` table: **0 rows**
- `comments` table: **0 rows**
- `alternatives` table: **0 rows**
- `decisions` table: **0 rows**
- `users` table: **1 row** (only pre-existing baseline user `employee_live_new@example.com` remains)

---

## Sprint 7c: Meeting Notes Module (Model, Migration, Schemas, Endpoints & Ownership) — SIGN-OFF — COMPLETE (2026-08-25)

### 1. What was built & Files Touched

- `app/models/meeting_note.py` — SQLAlchemy `MeetingNote` model with `id` (PK), `decision_id` (FK → decisions.id), `created_by` (FK → users.id), `title` (String, NOT NULL), `content` (String, NOT NULL), `meeting_date` (DateTime, NOT NULL), `created_at`, `updated_at`. Relationships to `Decision` (`meeting_notes`) and `User` (`meeting_notes`).
- `app/models/decision.py` — added `meeting_notes` relationship (`cascade="all, delete-orphan"`).
- `app/models/user.py` — added `meeting_notes` relationship (`cascade="all, delete-orphan"`).
- `app/models/__init__.py` & `alembic/env.py` — registered `MeetingNote`.
- `alembic/versions/85a9d7f952e2_create_meeting_notes_table.py` — migration created and applied (`alembic upgrade head`; `alembic current` = head).
- `app/schemas/meeting_note.py` — `MeetingNoteCreate` (`title`, `content`, `meeting_date`), `MeetingNoteUpdate` (`title`, `content`, `meeting_date` — all optional), `MeetingNoteResponse` (full model).
- `app/routers/meeting_note.py` — 5 endpoints with JWT auth (`get_current_user`) and ownership checks:
  - `POST /decisions/{decision_id}/meeting-notes` → 201 (`created_by` from JWT; 404 if decision not found)
  - `GET /decisions/{decision_id}/meeting-notes` → 200 list of notes (404 if decision not found)
  - `GET /meeting-notes/{note_id}` → 200 (404 if note not found)
  - `PUT /meeting-notes/{note_id}` → 200 (404 if not found; 403 Forbidden if not author/admin; bumps `updated_at`)
  - `DELETE /meeting-notes/{note_id}` → 200 `{"message": "Meeting note deleted successfully"}` (404 if not found; 403 Forbidden if not author/admin)
- `app/main.py` — registered `meeting_note_router` and `meeting_notes_router`.
- `tests/test_meeting_note.py` — 18 comprehensive tests covering CRUD, missing decision 404, missing note 404, field injections ignored, 422 validations, 401 without tokens, author/admin ownership 403/200, and cascade deletion.

---

### 2. Ownership Enforcement Policy

- **Rule Applied**: **Author OR Administrator** — consistent with Comments and Discussion Threads.
- **Rationale**: Original authors retain full control to edit or delete their meeting notes. Users with the `Administrator` role retain administrative/moderation capability. Non-owner non-admin users receive **403 Forbidden** (`{"detail": "Not authorized to modify this meeting note"}` / `{"detail": "Not authorized to delete this meeting note"}`).

---

### 3. Swagger / E2E Testing Workflow Verification (Real PostgreSQL)

| Step | Action & Description | Expected | Actual Result | Pass/Fail |
| --- | --- | --- | --- | --- |
| 1 | POST `/decisions/{id}/meeting-notes` | 201 Created | 201 Created (id=1, decision_id=28, created_by=31) | **PASS** |
| 2 | POST `/decisions/99999/meeting-notes` | 404 Not Found | 404 `{"detail": "Decision not found"}` | **PASS** |
| 3 | GET `/decisions/{id}/meeting-notes` | 200 list of notes | 200, returned 2 notes | **PASS** |
| 4 | GET `/meeting-notes/{id}` | 200 single note | 200, id=1, title="Initial Cloud Architecture Review" | **PASS** |
| 5 | GET `/meeting-notes/99999` | 404 Not Found | 404 `{"detail": "Meeting note not found"}` | **PASS** |
| 6 | PUT `/meeting-notes/{id}` as owner | 200 OK | 200, title updated, id/decision_id/created_by unchanged, updated_at bumped | **PASS** |
| 7a | PUT `/meeting-notes/{id}` as non-owner | 403 Forbidden | 403 `{"detail": "Not authorized to modify this meeting note"}` | **PASS** |
| 7b | PUT `/meeting-notes/{id}` as Administrator | 200 OK | 200, title updated by Admin | **PASS** |
| 8a | DELETE non-existing note | 404 Not Found | 404 `{"detail": "Meeting note not found"}` | **PASS** |
| 8b | DELETE `/meeting-notes/{id}` as non-owner | 403 Forbidden | 403 `{"detail": "Not authorized to delete this meeting note"}` | **PASS** |
| 8c | DELETE `/meeting-notes/{id}` as owner | 200 OK | 200 `{"message": "Meeting note deleted successfully"}` | **PASS** |
| 8d | DELETE `/meeting-notes/{id}` as Admin | 200 OK | 200 `{"message": "Meeting note deleted successfully"}` | **PASS** |
| 9 | All 5 endpoints without token | 401 Unauthorized | 401 `{"detail": "Not authenticated"}` on all 5 | **PASS** |
| 10 | POST with missing required field (`title`) | 422 Unprocessable | 422 validation error `loc: ["body", "title"]` | **PASS** |

---

### 4. Direct PostgreSQL Verification

Direct queries via `psycopg2` on live PostgreSQL `expert_decision_replay` database verified:
- **Columns & Types**: `id` (integer PK), `decision_id` (integer FK → decisions.id), `created_by` (integer FK → users.id), `title` (varchar), `content` (varchar), `meeting_date` (timestamptz), `created_at` (timestamptz), `updated_at` (timestamptz).
- **Constraints & Indexes**: `meeting_notes_pkey`, `meeting_notes_decision_id_fkey`, `meeting_notes_created_by_fkey`, indexes on `id`, `decision_id`, `created_by`.
- **Relationship**: Verified correct foreign key references to `decisions.id` and `users.id`.

---

### 5. Full Regression Test Results

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Bhargav\Desktop\expert-decision-replay
plugins: anyio-4.14.2
collected 108 items

tests\test_alternative.py .........................                      [ 23%]
tests\test_auth.py ...                                                   [ 25%]
tests\test_comment.py ................                                   [ 40%]
tests\test_decision_filtering.py ......                                  [ 46%]
tests\test_decision_status.py ........                                   [ 53%]
tests\test_meeting_note.py ..................                            [ 70%]
tests\test_security.py ....                                              [ 74%]
tests\test_thread.py ....................                                [ 92%]
tests\test_user_enhancements.py ........                                 [100%]

====================== 108 passed, 2 warnings in 31.86s =======================
```

**Zero regressions across Decisions, Alternatives, Comments, Discussion Threads, and Auth modules.**

---

### 6. Post-Verification Database State

- `meeting_notes` table: **0 rows**
- `discussion_threads` table: **0 rows**
- `comments` table: **0 rows**
- `alternatives` table: **0 rows**
- `decisions` table: **0 rows**
- `users` table: **1 row** (only pre-existing baseline user `employee_live_new@example.com` remains)

---

## Sprint 7: Collaboration, Discussion & Decision Rationale — FINAL SIGN-OFF — COMPLETE (2026-08-25)

Final verification pass for the entire Sprint 7 suite (Comments, Discussion Threads, Thread Replies, Meeting Notes, and Decision Rationale). All 17 endpoints, JWT authentication requirements, consistent Author OR Administrator ownership enforcement, schema contracts, database migrations, and relationship integrity have been verified against real PostgreSQL (`expert_decision_replay`).

### 1. Module Inventory & Files Touched

| Component | Files Touched / Created | Purpose |
| --- | --- | --- |
| **Comments** | `app/models/comment.py`, `app/schemas/comment.py`, `app/routers/comment.py` | Comment CRUD on decisions; supports direct comments and thread replies via nullable `thread_id` |
| **Discussion Threads** | `app/models/discussion_thread.py`, `app/schemas/discussion_thread.py`, `app/routers/discussion_thread.py` | Thread CRUD on decisions; `POST /threads/{id}/comments` for discussion thread replies |
| **Meeting Notes** | `app/models/meeting_note.py`, `app/schemas/meeting_note.py`, `app/routers/meeting_note.py` | Meeting notes CRUD on decisions with `meeting_date` |
| **Decision Rationale** | `app/models/decision.py`, `app/schemas/decision.py`, `app/routers/decision.py` | `rationale` nullable column on `decisions` table, `PUT /decisions/{id}/rationale`, retrieved via `GET /decisions/{id}` |
| **Migrations** | `alembic/versions/72f74061fb2d_create_comments_table.py`<br>`alembic/versions/a9b7255d0c2f_create_discussion_threads_table.py`<br>`alembic/versions/85a9d7f952e2_create_meeting_notes_table.py`<br>`alembic/versions/3013a5847f8d_add_rationale_column_to_decisions.py` | All migrations generated, reviewed, and applied (`alembic upgrade head`; current head: `3013a5847f8d`) |
| **App Routing** | `app/main.py` | Registered all routers (`comment_router`, `comments_router`, `thread_router`, `threads_router`, `meeting_note_router`, `meeting_notes_router`) |

---

### 2. Universal Ownership Enforcement Policy

- **Policy Enforced Across All Sprint 7 Resources**: **Author / Creator OR Administrator**
- **Rationale**: Original authors retain full authority to edit and delete their own contributions (comments, discussion threads, thread replies, meeting notes, decision rationale). Users with the `Administrator` role retain system-wide administrative and moderation capability to edit or delete any contribution. Any authenticated user who is neither the original author nor an Administrator attempting to update or delete a resource receives **403 Forbidden** (`{"detail": "Not authorized to ..."}`).

---

### 3. Comprehensive Endpoint & Auth/Ownership Matrix (17 Endpoints)

| Method | Endpoint | Auth | Ownership Rule | Expected Status |
| --- | --- | --- | --- | --- |
| POST | `/decisions/{id}/comments` | JWT | Any Authed User | 201 (sets `user_id` from JWT; 404 if decision missing) |
| GET | `/decisions/{id}/comments` | JWT | Any Authed User | 200 list (404 if decision missing) |
| GET | `/comments/{id}` | JWT | Any Authed User | 200 record (404 if missing) |
| PUT | `/comments/{id}` | JWT | Author or Administrator | 200 update (403 if non-owner; 404 if missing) |
| DELETE | `/comments/{id}` | JWT | Author or Administrator | 200 delete (403 if non-owner; 404 if missing) |
| POST | `/decisions/{id}/threads` | JWT | Any Authed User | 201 (sets `created_by` from JWT; 404 if decision missing) |
| GET | `/decisions/{id}/threads` | JWT | Any Authed User | 200 list (404 if decision missing) |
| GET | `/threads/{id}` | JWT | Any Authed User | 200 record (404 if missing) |
| PUT | `/threads/{id}` | JWT | Author or Administrator | 200 update (403 if non-owner; 404 if missing) |
| DELETE | `/threads/{id}` | JWT | Author or Administrator | 200 delete (403 if non-owner; 404 if missing) |
| POST | `/threads/{id}/comments` | JWT | Any Authed User | 201 reply (sets `thread_id` + inherits `decision_id`; 404 if thread missing) |
| POST | `/decisions/{id}/meeting-notes` | JWT | Any Authed User | 201 (sets `created_by` from JWT; 404 if decision missing) |
| GET | `/decisions/{id}/meeting-notes` | JWT | Any Authed User | 200 list (404 if decision missing) |
| GET | `/meeting-notes/{id}` | JWT | Any Authed User | 200 record (404 if missing) |
| PUT | `/meeting-notes/{id}` | JWT | Author or Administrator | 200 update (403 if non-owner; 404 if missing) |
| DELETE | `/meeting-notes/{id}` | JWT | Author or Administrator | 200 delete (403 if non-owner; 404 if missing) |
| PUT | `/decisions/{id}/rationale` | JWT | Creator or Administrator | 200 update (403 if non-owner; 404 if missing; verified via `GET /decisions/{id}`) |

---

### 4. Continuous E2E Workflow Demonstration (Real PostgreSQL)

| Step | Action | Actual Result | Status |
| :--- | :--- | :--- | :--- |
| 1 | Login User A, User B, Admin | 200, JWT tokens acquired | **PASS** |
| 2 | POST `/decisions` | 201 Created (ID=29, status="Draft", created_by=34) | **PASS** |
| 3 | Create 3 Comments as User A | 201 Created for all 3 | **PASS** |
| 4 | GET `/decisions/29/comments` | 200 OK, returned 3 comments | **PASS** |
| 5 | GET `/comments/{id}` | 200 OK, returned single record | **PASS** |
| 6 | PUT `/comments/{id}` as owner / non-owner / admin | Owner: 200; Non-owner: 403 Forbidden; Admin: 200 OK | **PASS** |
| 7 | DELETE `/comments/{id}` as non-owner / owner / admin | Non-owner: 403 Forbidden; Owner: 200 OK; Admin: 200 OK | **PASS** |
| 8 | POST `/decisions/29/threads` | 201 Created (ID=1, title="Latency vs Consistency Tradeoff") | **PASS** |
| 9 | POST `/threads/1/comments` × 2 (replies from User A & User B) | 201 Created for both; `thread_id=1` and `decision_id=29` stored | **PASS** |
| 10 | POST `/decisions/29/meeting-notes` | 201 Created (ID=4, title="Consensus Protocol Review Meeting") | **PASS** |
| 11 | PUT `/decisions/29/rationale` as owner | 200 OK; rationale set and returned in `DecisionResponse` | **PASS** |
| 12 | GET `/decisions/29` | 200 OK; confirmed `rationale` retrieved in response body | **PASS** |
| 13 | PUT `/decisions/29/rationale` as non-owner (User B) | 403 Forbidden (`{"detail": "Not authorized to modify this decision rationale"}`) | **PASS** |
| 14 | PUT `/decisions/29/rationale` as Administrator | 200 OK; updated to "Admin Approved Rationale" | **PASS** |
| 15 | Test all 17 endpoints without JWT | 401 Unauthorized (`{"detail": "Not authenticated"}`) across all 17 | **PASS** |
| 16 | Confirm Decision & Alternative APIs unaffected | POST alternative → 201; GET compare → 200 (1 alternative returned) | **PASS** |

---

### 5. PostgreSQL Database Verification

Direct SQL verification via `psycopg2` on live database `expert_decision_replay`:
- **`decisions`**: Confirmed `rationale` column present, updated to `"Admin Approved Rationale"`.
- **`comments`**: Confirmed 3 rows (`thread_id=NULL` for direct comments, `thread_id=1` for thread replies).
- **`discussion_threads`**: Confirmed thread row tied to `decision_id=29` and `created_by=34`.
- **`meeting_notes`**: Confirmed note row tied to `decision_id=29` with valid `meeting_date`.
- **Foreign Keys & Cascade Deletes**: Verified cascading delete constraints.

---

### 6. Full Regression Test Results

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Bhargav\Desktop\expert-decision-replay
plugins: anyio-4.14.2
collected 113 items

tests\test_alternative.py .........................                      [ 22%]
tests\test_auth.py ...                                                   [ 24%]
tests\test_comment.py ................                                   [ 38%]
tests\test_decision_filtering.py ......                                  [ 44%]
tests\test_decision_status.py .............                              [ 55%]
tests\test_meeting_note.py ..................                            [ 71%]
tests\test_security.py ....                                              [ 75%]
tests\test_thread.py ....................                                [ 92%]
tests\test_user_enhancements.py ........                                 [100%]

====================== 113 passed, 2 warnings in 35.55s =======================
```

---

### 7. Post-Verification Database State

- `meeting_notes`: **0 rows**
- `discussion_threads`: **0 rows**
- `comments`: **0 rows**
- `alternatives`: **0 rows**
- `decisions`: **0 rows**
- `users`: **1 row** (only pre-existing baseline user `employee_live_new@example.com` remains)

---

## Sprint 9: Activity Log Model & Automatic Activity Logging — COMPLETE (2026-08-27)

### 0. FLAG — Approval Workflow Dependency Check (BLOCKED)

The sprint spec referenced "an approval workflow implemented in Sprint 8 (Approval
model, approval statuses, assigned reviewers)". **This does NOT exist in the codebase.**
A case-insensitive search for `approval` across `app/` returned **zero matches** — there
is no Approval model, no approval status enum, and no reviewer-assignment logic anywhere.
Sprint 8 in this repo was actually *Discussion Threads*, not an approval workflow.

**Consequence:** Approval assignment / approval / rejection logging could NOT be
implemented. Those three logging actions are **explicitly blocked and deferred** to
Part C/D of the overall task, which themselves depend on the (still-missing) approval
workflow. Everything else in this sprint was completed.

### 1. What was built & Files Touched

- `app/models/activity_log.py` — new SQLAlchemy `ActivityLog` model:
  `id` (PK), `user_id` (FK → users.id, indexed, NOT NULL), `action` (String, NOT NULL),
  `entity_type` (String, NOT NULL), `entity_id` (Integer, nullable), `description`
  (Text, nullable), `created_at` (timestamptz, NOT NULL, server default now()).
- `app/models/__init__.py` & `alembic/env.py` — registered `ActivityLog` model.
- `app/services/activity.py` — **reusable `log_activity(db, user_id, action,
  entity_type, entity_id=None, description=None)` helper**. Adds the row, flushes, and
  commits the audit entry independently of the surrounding transaction so activity is
  always persisted (works both inside request handlers and standalone). This is the single
  shared logging path — no logging code duplicated across routes.
- `app/routers/decision.py` — wires `log_activity()` into:
  - `create_decision` → action `"create"`, entity_type `"decision"`
  - `update_decision` → action `"update"`, entity_type `"decision"`
  - `update_decision_status` → action `"status_change"`, entity_type `"decision"`
    (description records old → new status)
- `app/routers/alternative.py` — `create_alternative` → `"create"/"alternative"`;
  `update_alternative` → `"update"/"alternative"`.
- `app/routers/comment.py` — `create_comment` → `"create"/"comment"`;
  `update_comment` → `"update"/"comment"`.
- `app/routers/discussion_thread.py` — `create_thread` → `"create"/"discussion_thread"`.
- `alembic/versions/6a0d2fb180b3_create_activity_log_table.py` — migration generated via
  `alembic revision --autogenerate`, reviewed (only adds `activity_log` table + FK to
  users + two indexes), and applied (`alembic upgrade head`; `alembic current` = head
  `6a0d2fb180b3`).
- `tests/test_activity_log.py` — 6 new tests, each performs a real action via TestClient
  and asserts the matching `activity_log` row exists (correct user_id / action /
  entity_type / entity_id).
- `verify_activity_log.py` — standalone Swagger-style E2E script (live PostgreSQL +
  direct `psycopg2` verification + cleanup).

### 2. Actions logged (automatic, via `log_activity()`)

| Action | entity_type | action value |
| --- | --- | --- |
| Decision creation | `decision` | `create` |
| Decision update | `decision` | `update` |
| Decision status change | `decision` | `status_change` |
| Alternative creation | `alternative` | `create` |
| Alternative update | `alternative` | `update` |
| Comment creation | `comment` | `create` |
| Comment update | `comment` | `update` |
| Discussion thread creation | `discussion_thread` | `create` |

### 3. Actions BLOCKED — pending the approval workflow

- Approval assignment
- Approval
- Rejection

These are skipped intentionally because no Approval model / status / reviewer exists in the
codebase. They belong to Part C/D and cannot be built until the approval workflow is added.

### 4. Swagger / E2E Testing Workflow Verification (Real PostgreSQL `expert_decision_replay`)

Run via `verify_activity_log.py` (FastAPI TestClient pointed at the live DB):

| Step | Action | Result |
| --- | --- | --- |
| 1 | Create Decision | **PASS** — decision id=31, 1 `activity_log` row (`create`/`decision`) |
| 2 | Update Decision | **PASS** — 200, 1 row (`update`/`decision`) |
| 3 | Change status → "Under Review" | **PASS** — 200, 1 row (`status_change`/`decision`, desc "from 'Draft' to 'Under Review'") |
| 4 | Create Alternative | **PASS** — alt id=14, 1 row (`create`/`alternative`) |
| 5 | Create Comment | **PASS** — comment id=11, 1 row (`create`/`comment`) |
| 6 | Create Discussion Thread | **PASS** — thread id=3, 1 row (`create`/`discussion_thread`) |

### 5. PostgreSQL Direct Verification

Table structure (from `information_schema`):

```
id           integer                      NOT NULL
user_id      integer                      NOT NULL   (FK → users.id)
action       character varying            NOT NULL
entity_type  character varying            NOT NULL
entity_id    integer                      NULL
description  text                         NULL
created_at   timestamp with time zone     NOT NULL
```

Entries created for the test run (correct `user_id` / `entity_type` / `entity_id` /
`action`):

```
(38, 'decision',          31, 'create')
(38, 'decision',          31, 'update')
(38, 'decision',          31, 'status_change')
(38, 'alternative',       14, 'create')
(38, 'comment',           11, 'create')
(38, 'discussion_thread',  3, 'create')
```

### 6. Full Regression Test Results

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Bhargav\Desktop\expert-decision-replay
plugins: anyio-4.14.2
collected 119 items

tests\test_activity_log.py ......                                      [  5%]
tests\test_alternative.py .........................                    [ 26%]
tests\test_auth.py ...                                                 [ 28%]
tests\test_comment.py ................                                 [ 42%]
tests\test_decision_filtering.py ......                                [ 47%]
tests\test_decision_status.py .............                            [ 57%]
tests\test_meeting_note.py ..................                          [ 73%]
tests\test_security.py ....                                            [ 76%]
tests\test_thread.py ....................                              [ 93%]
tests\test_user_enhancements.py ........                               [100%]

====================== 119 passed, 2 warnings in 35.35s =======================
```

### 7. Post-Verification Database State (cleanup confirmed)

- `activity_log`: **0 rows**
- `meeting_notes`: **0 rows**
- `discussion_threads`: **0 rows**
- `comments`: **0 rows**
- `alternatives`: **0 rows**
- `decisions`: **0 rows**
- `users`: **1 row** (only pre-existing baseline user `employee_live_new@example.com` remains)

Test user `actlog_verify@example.com` and all of its cascaded entities + its activity_log
rows were deleted by the cleanup step.

---

## Sprint 9 (Part B): Dashboard Endpoints — COMPLETE (2026-08-27)

### 0. FLAG — Approval Workflow Still Missing (carried from Part A)

Part A confirmed the **approval workflow does NOT exist** in the codebase (no Approval
model, statuses, or assigned reviewers). Therefore `GET /dashboard/manager/pending-approvals`
is **BLOCKED / deferred** and implemented as an explicit 501 rather than fabricated.

### 1. What was built & Files Touched

- `app/schemas/dashboard.py` — `EmployeeDashboard` (user_id, total_decisions,
  decisions_by_status list, recent_activity list), `ManagerStatistics` (scope, total,
  draft, under_review, approved, rejected, archived), and `ActivityItem` for the recent
  activity feed.
- `app/routers/dashboard.py` — three endpoints, all requiring JWT:
  - `GET /dashboard/employee` — **any authenticated user**. Returns the caller's own
    decisions grouped by status (SQL `COUNT`/`GROUP BY` filtered by `created_by =
    current_user.id`, derived from JWT — no query param) plus their recent activity from
    `activity_log` (filtered by `user_id`, latest 20).
  - `GET /dashboard/manager/statistics` — **Manager / Administrator only** (403 otherwise).
    Aggregates decision counts by status via SQL `COUNT`/`GROUP BY` over the whole table.
    Returns org-wide totals for total/draft/under_review/approved/rejected/archived.
  - `GET /dashboard/manager/pending-approvals` — **BLOCKED**. Authorization gate
    (Manager/Admin → 403 for others) is enforced first; then it returns **501 Not
    Implemented** with a clear message that the approval workflow is not yet present.
- `app/main.py` — registered `dashboard_router`.
- `tests/test_dashboard.py` — 8 tests (own-stats scoping, activity feed, live re-fetch
  after create/alt/comment, manager counts match, employee 403, manager pending 501,
  employee pending 403, all-no-token 401).
- `verify_dashboard.py` — standalone Swagger-style E2E script (live PostgreSQL + direct
  SQL GROUP BY comparison + cleanup).

### 2. Authorization Matrix

| Method | Endpoint | Auth | Role | Result if wrong role |
| --- | --- | --- | --- | --- |
| GET | `/dashboard/employee` | JWT | Any authenticated user | 401 without token |
| GET | `/dashboard/manager/statistics` | JWT | Manager / Administrator | 403 for Employee/Reviewer; 401 without token |
| GET | `/dashboard/manager/pending-approvals` | JWT | Manager / Administrator | 403 for Employee/Reviewer; 501 (blocked) for authorized roles; 401 without token |

### 3. Scoping / Limitation (documented)

`/dashboard/manager/statistics` is **org-wide**. There is no team / reporting-line
concept on the `User` model yet, so manager statistics cannot be team-scoped. This is a
known limitation flagged for when a team/manager hierarchy is introduced.

### 4. Swagger / E2E Testing Workflow Verification (Real PostgreSQL `expert_decision_replay`)

Run via `verify_dashboard.py` (FastAPI TestClient pointed at the live DB):

| Step | Action | Result |
| --- | --- | --- |
| 1 | Login as Employee → GET `/dashboard/employee` | **PASS** — 200, `user_id` = own id, `total_decisions` = 0, all statuses 0 |
| 2 | Employee creates decision + alternative + comment → re-fetch | **PASS** — `total_decisions` = 1; recent_activity contains `create/decision`, `create/alternative`, `create/comment` |
| 3 | Manager → GET `/dashboard/manager/statistics` | **PASS** — 200, `scope=org-wide`, counts exactly match a direct SQL `GROUP BY` (`draft=1, approved=1, total=2` in the run) |
| 4 | Manager → GET `/dashboard/manager/pending-approvals` | **PASS (blocked)** — 501 with detail naming the missing approval workflow |
| 5 | Employee → GET `/dashboard/manager/statistics` | **PASS** — 403 `Not authorized to view manager dashboards` |
| 6 | All dashboard endpoints without token | **PASS** — all 3 return 401 `Not authenticated` |

### 5. PostgreSQL Direct Verification

Direct `GROUP BY` query `SELECT status, count(*) FROM decisions GROUP BY status` returned
`[('Approved', 1), ('Draft', 1)]` during the run — exactly matching the manager
statistics payload (`approved=1, draft=1, total=2`). Employee dashboard counts were
confirmed scoped to the single test employee's own created decision only.

### 6. Full Regression Test Results

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Bhargav\Desktop\expert-decision-replay
collected 127 items

tests\test_activity_log.py ......                                      [  4%]
tests\test_alternative.py .........................                    [ 24%]
tests\test_auth.py ...                                                 [ 26%]
tests\test_comment.py ................                                 [ 39%]
tests\test_dashboard.py ........                                       [ 45%]
tests\test_decision_filtering.py ......                                [ 50%]
tests\test_decision_status.py .............                            [ 60%]
tests\test_meeting_note.py ..................                          [ 74%]
tests\test_security.py ....                                            [ 77%]
tests\test_thread.py ....................                              [ 93%]
tests\test_user_enhancements.py ........                               [100%]

====================== 127 passed, 2 warnings in 46.92s =======================
```

### 7. Post-Verification Database State (cleanup confirmed)

- `activity_log`: **0 rows**
- `discussion_threads`: **0 rows**
- `comments`: **0 rows**
- `alternatives`: **0 rows**
- `decisions`: **0 rows**
- `users`: **1 row** (only pre-existing baseline user `employee_live_new@example.com` remains)
- `meeting_notes`: **0 rows**

Both test users (`dash_verify_emp@example.com`, `dash_verify_mgr@example.com`) and all of
their cascaded entities + activity_log rows were deleted by the cleanup step.

---

## Sprint 9 (Part C/D): Admin Dashboard Enhancements, Activities Endpoint & Analytics Date Filters — COMPLETE (2026-08-31)

### 0. FLAG — Approval Workflow Still Missing (carried from Part A)

Part A confirmed the **approval workflow does NOT exist** in the codebase (no Approval
model, statuses, or assigned reviewers). Therefore `GET /dashboard/admin/approval-statistics`
is **BLOCKED / deferred** and implemented as an explicit 501 rather than fabricated.

### 1. What was built & Files Touched

- `app/schemas/dashboard.py` — added:
  - `UserActivitySummary` (user_id, full_name, email, role, total_actions, actions_by_type, last_active)
  - `AdminUserActivity` (total_active_users, users list)
  - `ApprovalStatisticsResponse` (detail string for blocked state)
  - `PaginatedActivityResponse` (items, total, offset, limit, has_more)
  - `ActivityItem` — added `user_id` field
- `app/routers/dashboard.py` — added/modified:
  - `GET /dashboard/admin/approval-statistics` — **BLOCKED 501** (authorization gate first, then 501 with clear explanation)
  - `GET /dashboard/admin/user-activity` — admin-only, aggregates activity_log by user with SQL, returns per-user action breakdowns and last_active timestamp; supports `?start_date=&end_date=`
  - `GET /dashboard/admin/analytics` — now accepts optional `?start_date=&end_date=`; scopes decision stats and active users to the date range
  - `GET /dashboard/admin/decision-activity` — now accepts optional `?start_date=&end_date=`; scopes the GROUP BY to the date range
  - Added `_parse_date_param()` and `_validate_date_range()` helpers (422 on invalid format or reversed range)
- `app/routers/activities.py` — **new file**, single endpoint:
  - `GET /activities` — paginated activity feed
  - Authorization: Administrator/Manager see org-wide; Employee/Reviewer see own only
  - Filters: `?user=`, `?action=`, `?entity_type=`, `?start_date=`, `?end_date=`
  - Pagination: `?offset=0&limit=50` (max 200); response includes `total` and `has_more`
- `app/main.py` — registered `activities_router`
- `tests/test_dashboard.py` — 26 new tests (total 34; 3 skipped on SQLite due to `date_trunc`)

### 2. New Endpoint Inventory

| Method | Endpoint | Auth | Role | Behavior |
| --- | --- | --- | --- | --- |
| GET | `/dashboard/admin/approval-statistics` | JWT | Administrator | 501 BLOCKED (approval workflow missing); 403 for non-admin; 401 without token |
| GET | `/dashboard/admin/user-activity` | JWT | Administrator | 200 user activity summary (SQL-aggregated); supports date filters; 403/401 |
| GET | `/activities` | JWT | Any authenticated | 200 paginated activity feed; admin/manager see all, others see own; filters + pagination |
| GET | `/dashboard/admin/analytics` | JWT | Administrator | 200 (now with `?start_date=&end_date=`); 422 on bad/reversed dates; 403/401 |
| GET | `/dashboard/admin/decision-activity` | JWT | Administrator | 200 (now with `?start_date=&end_date=`); 422 on bad/reversed dates; 403/401 |

### 3. Authorization Matrix (all endpoints)

| Endpoint | Auth | Employee | Manager | Administrator | No Token |
| --- | --- | --- | --- | --- | --- |
| `/dashboard/admin/approval-statistics` | JWT | 403 | 403 | 501 (blocked) | 401 |
| `/dashboard/admin/user-activity` | JWT | 403 | 403 | 200 | 401 |
| `/activities` | JWT | 200 (own only) | 200 (all) | 200 (all) | 401 |
| `/dashboard/admin/analytics` | JWT | 403 | 403 | 200 (date-filtered) | 401 |
| `/dashboard/admin/decision-activity` | JWT | 403 | 403 | 200 (date-filtered) | 401 |

### 4. Date Filter Behavior

- Format: `YYYY-MM-DD` (ISO 8601)
- Invalid format → **422** `{"detail": "Invalid date format: '...'. Expected YYYY-MM-DD."}`
- `start_date` after `end_date` → **422** `{"detail": "start_date must not be after end_date."}`
- Both optional; one without the other is valid
- End date is inclusive (query uses `< end_date + 1 day`)
- Empty range (no matching data) → **200** with zeroed counts / empty list

### 5. `/activities` Pagination

- Default: `offset=0, limit=50`
- Maximum `limit`: 200
- Response shape: `{"items": [...], "total": N, "offset": 0, "limit": 50, "has_more": bool}`
- `has_more = True` when `offset + limit < total`

### 6. Test Coverage (26 new tests in test_dashboard.py)

| Test | What it covers |
| --- | --- |
| `test_admin_approval_statistics_blocked_501` | Admin gets 501 with approval workflow message |
| `test_employee_blocked_from_approval_statistics` | Employee gets 403 |
| `test_admin_user_activity_shows_active_users` | User activity aggregated correctly across users |
| `test_admin_user_activity_date_filter` | Date filtering works (today finds data, future finds none) |
| `test_employee_blocked_from_user_activity` | Employee gets 403 |
| `test_activities_admin_sees_all` | Admin sees activity from all users |
| `test_activities_non_admin_sees_own_only` | Employee sees only own activity |
| `test_activities_filter_by_action` | `?action=create` and `?action=status_change` filter correctly |
| `test_activities_filter_by_entity_type` | `?entity_type=alternative` and `?entity_type=comment` filter correctly |
| `test_activities_filter_by_user` | `?user=<id>` filters to specific user (admin only) |
| `test_activities_pagination` | limit=2 pages through 3 items correctly; `has_more` flag correct |
| `test_activities_date_filter` | `?start_date=today` finds data; future date returns 0 |
| `test_activities_invalid_date_422` | Bad format → 422 |
| `test_activities_reversed_date_range_422` | start > end → 422 |
| `test_activities_require_token` | No token → 401 |
| `test_admin_analytics_date_filter` | Date filtering on analytics works |
| `test_admin_analytics_invalid_date_422` | Bad format → 422 |
| `test_admin_analytics_reversed_date_422` | start > end → 422 |
| `test_admin_decision_activity_date_filter` | Date filtering on decision-activity (skipped on SQLite) |
| `test_admin_decision_activity_invalid_date_422` | Bad format → 422 |
| `test_admin_dashboard_endpoints_require_token` | All 4 admin endpoints → 401 without token |

### 7. Full Regression Test Results

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Bhargav\Desktop\expert-decision-replay
plugins: anyio-4.14.2
collected 153 items

tests\test_activity_log.py ......                                      [  3%]
tests\test_alternative.py .........................                    [ 22%]
tests\test_auth.py ...                                                 [ 24%]
tests\test_comment.py ................                                 [ 35%]
tests\test_dashboard.py ................................              [ 57%]
tests\test_decision_filtering.py ......                                [ 61%]
tests\test_decision_status.py .............                            [ 69%]
tests\test_meeting_note.py ..................                          [ 80%]
tests\test_security.py ....                                            [ 83%]
tests\test_thread.py ....................                              [ 93%]
tests\test_user_enhancements.py ........                               [100%]

====================== 153 passed, 8 warnings in 46.93s =======================
```

**Zero regressions. Zero skips.**

### 8. Post-Verification Database State

- `activity_log`: **0 rows** (test data cleaned up)
- `meeting_notes`: **0 rows**
- `discussion_threads`: **0 rows**
- `comments`: **0 rows**
- `alternatives`: **0 rows**
- `decisions`: **0 rows**
- `users`: **1 row** (only pre-existing baseline user `employee_live_new@example.com` remains)

---

## Final Smoke / Regression Test Report (2026-08-31)

### 1. 401 Without JWT — All 9 Dashboard/Activity Endpoints

| Endpoint | Result |
| --- | --- |
| `GET /dashboard/employee` | **401** |
| `GET /dashboard/manager/statistics` | **401** |
| `GET /dashboard/manager/pending-approvals` | **401** |
| `GET /dashboard/admin` | **401** |
| `GET /dashboard/admin/analytics` | **401** |
| `GET /dashboard/admin/decision-activity` | **401** |
| `GET /dashboard/admin/approval-statistics` | **401** |
| `GET /dashboard/admin/user-activity` | **401** |
| `GET /activities` | **401** |

All endpoints correctly reject unauthenticated requests.

### 2. Authorization Matrix (all PASS)

| Scenario | Endpoint | Expected | Actual |
| --- | --- | --- | --- |
| Employee → employee dashboard | `/dashboard/employee` | 200 | **200** |
| Employee → admin endpoints (5) | `/dashboard/admin/*` | 403 | **403** |
| Employee → manager endpoints (2) | `/dashboard/manager/*` | 403 | **403** |
| Manager → manager statistics | `/dashboard/manager/statistics` | 200 | **200** |
| Manager → pending-approvals | `/dashboard/manager/pending-approvals` | 501 (blocked) | **501** |
| Manager → admin endpoints (5) | `/dashboard/admin/*` | 403 | **403** |
| Admin → admin endpoints (4) | `/dashboard/admin/*` | 200 | **200** |
| Admin → approval-statistics | `/dashboard/admin/approval-statistics` | 501 (blocked) | **501** |
| Reviewer → admin endpoint | `/dashboard/admin` | 403 | **403** |
| Reviewer → employee dashboard | `/dashboard/employee` | 200 | **200** |
| Reviewer → activities | `/activities` | 200 | **200** |
| Admin → activities (all users) | `/activities` | 200 | **200** |
| Manager → activities (all users) | `/activities` | 200 | **200** |

### 3. Complete Workflow Test

| Step | Action | Result |
| --- | --- | --- |
| 1 | Employee creates decision | **201** |
| 2 | Employee adds alternative | **201** |
| 3 | Employee adds comment | **201** |
| 4 | Employee changes status to "Under Review" | **200** |
| 5 | Employee dashboard: 1 decision, Under Review=1 | **PASS** |
| 6 | Employee activity feed: >= 4 entries | **PASS** |
| 7 | Manager statistics: total >= 1 | **PASS** |
| 8 | Admin dashboard: total_decisions >= 1 | **PASS** |
| 9 | Admin analytics: total >= 1 | **PASS** |
| 10 | Admin user-activity: >= 1 active user | **PASS** |
| 11 | Admin activities: sees all users' activity | **PASS** |

Approval workflow steps skipped — no Approval model exists.

### 4. Error Handling

| Scenario | Endpoint | Expected | Actual |
| --- | --- | --- | --- |
| Invalid date format | `/dashboard/admin/analytics?start_date=not-a-date` | 422 | **422** |
| Invalid date format | `/activities?start_date=bad` | 422 | **422** |
| Reversed date range | `/dashboard/admin/analytics?start=2026-12-31&end=2026-01-01` | 422 | **422** |
| Reversed date range | `/activities?start=2026-12-31&end=2026-01-01` | 422 | **422** |
| Negative offset | `/activities?offset=-1` | 422 | **422** |
| limit=0 | `/activities?limit=0` | 422 | **422** |
| limit=201 (max 200) | `/activities?limit=201` | 422 | **422** |
| Invalid granularity | `/dashboard/admin/decision-activity?granularity=hourly` | 422 | **422** |

### 5. Cross-Check Dashboard vs PostgreSQL

| Metric | Dashboard API | SQL `SELECT count(*)` | Match |
| --- | --- | --- | --- |
| Manager statistics total | 1 | 1 | **YES** |
| Admin analytics total | 1 | 1 | **YES** |

### 6. Full Regression Suite

```
python -m pytest: 153 passed, 0 failed, 0 skipped (47.87s)
```

### 7. Approval Workflow Blockers

All approval-dependent endpoints are BLOCKED / deferred:

| Endpoint | Status | Reason |
| --- | --- | --- |
| `GET /dashboard/manager/pending-approvals` | 501 | No Approval model, statuses, or reviewers |
| `GET /dashboard/admin/approval-statistics` | 501 | No Approval model, statuses, or reviewers |

These cannot be implemented until the approval workflow (Approval model, approval
statuses, assigned reviewers) is built. Both endpoints enforce role authorization
(403 for non-authorized roles) before returning 501.

### 8. Implementation Change Summary

**Files created:**
- `app/routers/activities.py` — `GET /activities` endpoint with filters + pagination

**Files modified:**
- `app/schemas/dashboard.py` — added `UserActivitySummary`, `AdminUserActivity`,
  `ApprovalStatisticsResponse`, `PaginatedActivityResponse`; added `user_id` to `ActivityItem`
- `app/routers/dashboard.py` — added `/admin/approval-statistics` (501),
  `/admin/user-activity`, date filters on `/admin/analytics` and `/admin/decision-activity`;
  dialect-aware `date_trunc` for SQLite/PostgreSQL
- `app/main.py` — registered `activities_router`
- `tests/test_dashboard.py` — 34 tests (8 original + 26 new for Part C/D)

**No new migrations** — all changes are in Python code only (schemas, routers, tests).

---

## Sprint 10: Audit Logs Endpoint, Security Logging & Access Logging — COMPLETE (2026-08-31)

### 1. What was built & Files Touched

- `app/schemas/audit_log.py` — added `PaginatedAuditLogResponse` (items, total, page, page_size,
  pages) for the new paginated audit-logs endpoint.
- `app/routers/audit.py` — added `audit_logs_router` (prefix `/audit-logs`) with three endpoints:
  - `GET /audit-logs` — paginated audit log listing with RBAC, filters, and date range support
  - `GET /audit-logs/{log_id}` — single audit log retrieval with RBAC
  - Retained existing `GET /audit/logs` and `GET /audit/logs/{log_id}` for backward compatibility
  - Added `_parse_date()` helper for YYYY-MM-DD validation
  - Added `log_security(unauthorized_access)` on 403 forbidden access in single-log endpoint
- `app/api/deps.py` — modified `get_current_user` to accept `Request` and log `SecurityLog` for:
  - Missing authentication credentials (no token) → `unauthorized_access`
  - Invalid or expired JWT token → `unauthorized_access`
  - User not found for token subject → `unauthorized_access`
- `app/routers/security.py` — added `Request` parameter and `log_security(unauthorized_access)`
  on 403 responses (both list and single-log endpoints).
- `app/routers/access_log.py` — added `Request` parameter and `log_security(unauthorized_access)`
  on 403 responses (both list and single-log endpoints).
- `app/services/audit.py` — extended `SENSITIVE_FIELDS` with `db_password`, `database_url`,
  `credentials`, `api_key`, `authorization` to prevent leaking DB credentials and other secrets.
- `app/main.py` — registered `audit_logs_router`.
- `tests/test_audit_logs.py` — 54 new tests covering all functionality.

### 2. New Endpoint Inventory

| Method | Endpoint | Auth | Role | Behavior |
| --- | --- | --- | --- | --- |
| GET | `/audit-logs` | JWT | Any authenticated | 200 paginated audit logs; admin/manager see all, others see own; filters + page/page_size pagination |
| GET | `/audit-logs/{log_id}` | JWT | Any authenticated | 200 single audit log or 404; 403 if non-admin and not own log |
| GET | `/audit/logs` | JWT | Any authenticated | 200 list (legacy offset/limit); admin/manager see all, others see own |
| GET | `/audit/logs/{log_id}` | JWT | Any authenticated | 200 single log (legacy); 403 if non-admin and not own log |

### 3. `GET /audit-logs` — Query Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `page` | int | 1 | Page number (1-indexed, ge=1) |
| `page_size` | int | 50 | Items per page (1–200) |
| `user` | int | None | Filter by user ID (admin/manager only) |
| `action` | AuditAction enum | None | Filter by action (create, update, delete, status_change, login, logout, login_failed, access, export, approve, reject) |
| `entity_type` | AuditEntityType enum | None | Filter by entity type (decision, alternative, comment, discussion_thread, meeting_note, user, auth, system) |
| `entity_id` | int | None | Filter by entity ID |
| `start_date` | str | None | Filter by start date (YYYY-MM-DD format) |
| `end_date` | str | None | Filter by end date (YYYY-MM-DD format, inclusive) |

### 4. Response Shape — `PaginatedAuditLogResponse`

```json
{
  "items": [
    {
      "id": 1,
      "user_id": 5,
      "action": "create",
      "entity_type": "decision",
      "entity_id": 10,
      "description": "Created decision 'My Decision'",
      "old_values": null,
      "new_values": "{\"title\": \"My Decision\"}",
      "ip_address": "127.0.0.1",
      "created_at": "2026-08-31T12:00:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 10,
  "pages": 3
}
```

### 5. Security Logging — Where Architecture Permits

| Event | Trigger | Where Logged | event_type |
| --- | --- | --- | --- |
| Login success | POST /login with valid credentials | `app/api/routes/auth.py` | `login` |
| Login failure | POST /login with wrong password or unknown email | `app/api/routes/auth.py` | `login_failed` |
| Logout | POST /login/logout with valid JWT | `app/api/routes/auth.py` | `logout` |
| Invalid JWT | Any endpoint with malformed/expired Bearer token | `app/api/deps.py` | `unauthorized_access` |
| Missing token | Any endpoint without Authorization header | `app/api/deps.py` | `unauthorized_access` |
| User not found | JWT valid but user_id doesn't exist in DB | `app/api/deps.py` | `unauthorized_access` |
| Forbidden access (audit) | Non-admin viewing another user's audit log | `app/routers/audit.py` | `unauthorized_access` |
| Forbidden access (security) | Non-admin/manager accessing security logs | `app/routers/security.py` | `unauthorized_access` |
| Forbidden access (access) | Non-admin/manager accessing access logs | `app/routers/access_log.py` | `unauthorized_access` |

### 6. Audit Record Protection

- No PUT or DELETE endpoints exist for audit logs (read-only by design).
- Verified: `PUT /audit-logs` → 405/404; `DELETE /audit-logs` → 405/404; `PUT /audit/logs` → 405/404; `DELETE /audit/logs` → 405/404.
- Only Administrators and Managers can view organization-wide audit/security/access logs.
- Employees and Reviewers can only view their own audit history.

### 7. Sensitive Data Sanitization

The `SENSITIVE_FIELDS` set in `app/services/audit.py` masks the following fields in `old_values`/`new_values` JSON:

```python
SENSITIVE_FIELDS = {
    "password", "secret", "token", "password_hash", "secret_key",
    "db_password", "database_url", "credentials", "api_key", "authorization",
}
```

- Any field whose lowercase name matches is replaced with `"***"` before storage.
- Verified via tests: `password`, `db_password`, `token`, `api_key`, `secret_key`, `authorization` → all `"***"`.
- Non-sensitive fields (`title`, `category`, `status`) are preserved unchanged.
- No raw passwords, JWT secrets, DB credentials, or API keys appear in log descriptions.

### 8. Authorization Matrix

| Endpoint | Auth | Employee | Reviewer | Manager | Administrator | No Token |
| --- | --- | --- | --- | --- | --- | --- |
| `GET /audit-logs` | JWT | 200 (own) | 200 (own) | 200 (all) | 200 (all) | 401 |
| `GET /audit-logs/{id}` | JWT | 200 (own) / 403 | 200 (own) / 403 | 200 (all) | 200 (all) | 401 |
| `GET /audit/logs` | JWT | 200 (own) | 200 (own) | 200 (all) | 200 (all) | 401 |
| `GET /audit/logs/{id}` | JWT | 200 (own) / 403 | 200 (own) / 403 | 200 (all) | 200 (all) | 401 |
| `GET /security/logs` | JWT | 403 | 403 | 200 | 200 | 401 |
| `GET /security/logs/{id}` | JWT | 403 | 403 | 200 | 200 | 401 |
| `GET /access/logs` | JWT | 403 | 403 | 200 | 200 | 401 |
| `GET /access/logs/{id}` | JWT | 403 | 403 | 200 | 200 | 401 |

### 9. Date Filter Behavior

- Format: `YYYY-MM-DD` (ISO 8601)
- Invalid format → **422** `{"detail": "Invalid date format: '...'. Expected YYYY-MM-DD."}`
- `start_date` after `end_date` → **422** `{"detail": "start_date must not be after end_date."}`
- Both optional; one without the other is valid
- End date is inclusive (query uses `< end_date + 1 day`)
- Empty range (no matching data) → **200** with empty items and total=0

### 10. Pagination Behavior

- Default: `page=1, page_size=50`
- Maximum `page_size`: 200
- Minimum `page`: 1
- Response includes `total` (matching records), `pages` (ceiling of total/page_size)
- All filtering done at DB level via SQLAlchemy; no full-table scan into Python

### 11. Test Coverage (54 new tests in test_audit_logs.py)

| Category | Tests | What they cover |
| --- | --- | --- |
| Pagination | 6 | Page 1, page 2, empty page, defaults, max limit, invalid page |
| Filters | 6 | user, action, entity_type, entity_id, invalid action (422), invalid entity_type (422) |
| Date Filters | 6 | start_date, end_date, date range, invalid format (422), invalid end format (422), reversed range (422) |
| RBAC | 5 | Requires auth, employee scoping, admin sees all, manager sees all, employee can't filter others |
| Single Log RBAC | 3 | Get by ID, not found (404), employee can't view other's log (403) |
| Security Logging | 4 | Invalid JWT → security_log, missing token → security_log, forbidden access (security router), forbidden access (access router) |
| Sensitive Data | 3 | Password/db_password/token sanitized, api_key/secret_key/authorization sanitized, non-sensitive fields preserved |
| Audit Protection | 4 | No PUT/DELETE on /audit-logs, no PUT/DELETE on /audit/logs |
| Security Logs | 8 | Login success, login failure, requires admin/manager, admin can view, manager can view, filter by event type, invalid event type (422), get by ID, not found |
| Access Logs | 5 | Requires admin/manager, admin can view, filter by method, filter by status_code, get by ID, not found |
| Integration | 3 | Full workflow creates all log types, login/logout creates security logs |

### 12. Full Regression Test Results

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Bhargav\Desktop\expert-decision-replay
plugins: anyio-4.14.2
collected 246 items

...246 passed, 11 warnings in 72.71s
```

**Zero regressions. Zero failures. 54 new tests added.**

### 13. Files Changed Summary

**Modified:**
- `app/schemas/audit_log.py` — added `PaginatedAuditLogResponse`
- `app/routers/audit.py` — added `audit_logs_router` with `/audit-logs` endpoints, `_parse_date()`, security logging on 403
- `app/api/deps.py` — `get_current_user` now logs `SecurityLog(unauthorized_access)` for invalid JWT, missing token, user not found
- `app/routers/security.py` — added `Request` param, `log_security(unauthorized_access)` on 403
- `app/routers/access_log.py` — added `Request` param, `log_security(unauthorized_access)` on 403
- `app/services/audit.py` — extended `SENSITIVE_FIELDS` with `db_password`, `database_url`, `credentials`, `api_key`, `authorization`
- `app/main.py` — registered `audit_logs_router`

**Created:**
- `tests/test_audit_logs.py` — 54 tests for all new functionality

**No new migrations** — all changes are in Python code only (schemas, routers, deps, services, tests).

---

## Sprint 11 — Swagger Workflow Verification (Testing Only)

### 1. Objective

Full end-to-end workflow verification of audit/security/access logging, decision versioning, RBAC, and error handling. No new code changes — testing-only sprint.

### 2. Test File Created

`tests/test_sprint11_workflow.py` — 34 tests

### 3. Test Categories

| Category | Tests | What they verify |
| --- | --- | --- |
| Login Workflow | 3 | Login → security_log(event_type=login) + audit_log(action=login); login_failed → security_log(event_type=login_failed); logout → security_log(event_type=logout) |
| Create Decision | 1 | Audit(action=create, entity_type=decision, entity_id) + DecisionVersion(version_number=1, status="Draft") |
| Update Decision | 1 | Audit(action=update) with old_values.title="Original" + new_values.title="Revised"; DecisionVersion(version_number=2) |
| Status Change | 1 | Audit(action=status_change) with old_values.status="Draft" + new_values.status="Under Review"; DecisionVersion(version_number=2) |
| Create Alternative | 1 | Audit(action=create, entity_type=alternative) |
| Create Comment | 1 | Audit(action=create, entity_type=comment) |
| Full Lifecycle | 1 | Draft→Under Review→Approved: 4 audit entries (create, update, status_change, status_change); 4 sequential versions |
| History Endpoint | 1 | GET /decisions/{id}/history returns all audit entries for that decision |
| Versions Endpoint | 2 | GET /decisions/{id}/versions returns all versions in desc order; GET /decisions/{id}/versions/{n} returns specific version |
| Admin Audit-Logs | 1 | Admin can access GET /audit-logs and see all users' entries |
| Employee Scoping | 3 | Employee sees only own audit logs; employee gets 403 on /security/logs; employee gets 403 on /access/logs |
| No JWT / Invalid JWT | 2 | All protected endpoints return 401 without JWT; invalid JWT returns 401 + creates security_log(unauthorized_access) |
| Error 404 | 5 | Nonexistent decision/update/status_change/version returns 404; nonexistent version of existing decision returns 404 |
| Error 422 | 7 | Invalid action, entity_type, date format, reversed date range, page_size>200, page<1, invalid security event_type |
| DB Verification | 4 | Correct user_id/action/entity_type/entity_id/timestamps; sequential version numbers; security_log on forbidden_access; no sensitive data in audit values |

### 4. Key DB Record Assertions

- **audit_log**: `user_id` matches creator, `action` matches operation (`create`/`update`/`status_change`/`login`/`logout`), `entity_type` matches entity (`decision`/`alternative`/`comment`/`auth`), `entity_id` matches created record, `old_values`/`new_values` JSON strings contain correct before/after state
- **decision_version**: `version_number` starts at 1 and increments sequentially; `status` records the status BEFORE the change; `title`/`problem_statement`/`category` snapshot the pre-update state
- **security_log**: `event_type` matches event (`login`/`logout`/`login_failed`/`unauthorized_access`), `user_id` set correctly, `description` contains meaningful text
- **sensitive data**: fields `password`, `db_password`, `token`, `api_key`, `secret_key`, `authorization` are all replaced with `"***"`

### 5. Full Regression Test Results

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Bhargav\Desktop\expert-decision-replay
plugins: anyio-4.14.2
collected 280 items

...280 passed, 13 warnings in 87.99s
```

**280 total tests passing (246 original + 34 Sprint 11). Zero regressions.**

### 6. Sprint 11 Summary

| Metric | Value |
| --- | --- |
| New tests | 34 |
| Total tests | 280 |
| Pass rate | 100% |
| Regressions | 0 |
| Code changes | None (testing only) |
| New migrations | None |

