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
