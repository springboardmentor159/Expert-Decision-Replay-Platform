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
