
# AGENT_01_FOUNDATION

## Objective

Stand up the repository skeleton, database models, migrations, seed data, configuration, and the import-graph lint that every other agent depends on. This is the Day 0 gate — nothing else meaningfully starts until this is done.

## Scope

- Repository/directory skeleton per `02_SYSTEM_ARCHITECTURE.md` §2
- SQLAlchemy 2.0 models for every table in `05_DATA_MODEL.md`
- Migration setup (Alembic or equivalent) producing a clean `upgrade head` on a fresh SQLite file
- `app/core`: config loader (`.env` via pydantic-settings or equivalent), DB session management, shared enums (`DecisionType`, `CampaignStatus`, `OrderStatus`, etc.), base auth dependency (JWT bearer token parsing per `04_API_CONTRACTS.md` §Auth)
- Seed script (`app/seed.py`) per `19_ENVIRONMENT_SETUP.md` §7
- `scripts/check_import_graph.py` implementing the rules in `14_TEST_PLAN.md` §3
- `.env.example` and `frontend/.env.local.example`
- `requirements.txt` / `package.json` skeletons (no unnecessary dependencies — see `01_PRODUCT_SPEC.md` §7)

## Files/Directories Owned

`backend/app/core/`, `backend/app/models/` (or models colocated per package — decide and document consistently), `backend/alembic/` (or chosen migration tool), `backend/app/seed.py`, `scripts/check_import_graph.py`, `backend/requirements.txt`, root `.env.example`, `frontend/.env.local.example`, `frontend/package.json` skeleton, root `CHANGELOG.md` (initialize empty with header).

## Dependencies

None — this is the first task.

## Interfaces/Contracts Produced

- Every model class matching `05_DATA_MODEL.md` field-for-field (names, types, nullability)
- `app/core/config.py: Settings` object exposing every variable in `19_ENVIRONMENT_SETUP.md` §5
- `app/core/db.py: get_session()` async context manager/dependency
- `app/core/auth.py: get_current_user()` FastAPI dependency returning `{sub, role}`

## Implementation Requirements

1. Every table from `05_DATA_MODEL.md` exists with correct types; monetary fields are integers.
2. Migrations run cleanly from empty on `sqlite+aiosqlite`.
3. Seed script is idempotent (safe to re-run — either upserts or clears+reloads).
4. Import-graph lint script hard-codes the rules from `14_TEST_PLAN.md` §3 and exits non-zero on violation; it must correctly pass on an otherwise-empty skeleton and correctly fail on a deliberately-introduced violation (write a throwaway test file to prove this, then remove it).
5. Config loader fails loudly (not silently defaults) if a required secret is missing.

## Tests Required

- `test_migrations_run_clean.py`
- `test_seed_idempotent.py` — running seed twice doesn't duplicate rows or error
- `test_import_graph_lint.py` — asserts the lint script correctly flags a deliberately-broken sample import

## Acceptance Criteria

- [ ] `alembic upgrade head` succeeds on a fresh DB file
- [ ] `python -m app.seed` populates all seed data from `19_ENVIRONMENT_SETUP.md` §7, including the malicious-content fixture product
- [ ] `python scripts/check_import_graph.py` runs and passes on the skeleton
- [ ] `pytest` runs (even with few tests) with zero errors
- [ ] `.env.example` documents every variable other agents will need

## Must NOT Modify

Nothing yet exists for other agents to conflict with — but going forward, once other agents' packages exist, AGENT_01 must not modify `app/catalog`, `app/guardian`, `app/commerce_agent`, `app/campaign`, `app/razorpay_adapter`, `app/receipts`, `app/security`, `app/ai_provider`, or `frontend/` business logic without a flagged `[CONTRACT-CHANGE]`.
