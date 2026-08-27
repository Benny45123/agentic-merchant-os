
# 17 — Multi-Agent Development Workflow

## 1. Principle

Every Gemini CLI agent owns a directory subtree and a corresponding `AGENT_TASKS/AGENT_0X_*.md` file. Agents work against **frozen contracts** (`04_API_CONTRACTS.md`, `05_DATA_MODEL.md`), not against each other's in-progress code. This lets Day 1-6 work happen largely in parallel.

## 2. Git / Worktree Strategy

**Branching model:** trunk-based with short-lived per-agent branches.

```
main                                  (always runnable, protected)
 ├─ agent/01-foundation
 ├─ agent/02-catalog
 ├─ agent/03-commerce-agent
 ├─ agent/04-guardian
 ├─ agent/05-razorpay
 ├─ agent/06-receipts
 ├─ agent/07-campaign
 ├─ agent/08-frontend
 ├─ agent/09-security
 └─ agent/10-integration
```

Because multiple Gemini CLI agents may run **concurrently on the same machine**, use `git worktree` so each agent has an isolated working directory without repeated clone/checkout thrashing:

```
git worktree add ../amos-agent01 agent/01-foundation
git worktree add ../amos-agent02 agent/02-catalog
...
```

Each worktree is a full checkout on its own branch; agents never `git checkout` inside a shared directory mid-task.

## 3. Merge Order (follows the dependency graph in `16_DEVELOPMENT_PLAN_10_DAYS.md`)

1. `agent/01-foundation` → `main` (Day 0, gate: import lint + migrations run)
2. `agent/02-catalog`, mandate/policy portion of `agent/04-guardian` → `main` (Day 1)
3. `agent/04-guardian` (core), `agent/05-razorpay` → `main` (Day 2)
4. `agent/06-receipts`, `agent/03-commerce-agent` → `main` (Day 3)
5. Day 4 integration commits directly building on `main`
6. `agent/08-frontend`, `agent/09-security` → `main` (Day 5)
7. `agent/07-campaign` → `main` (Day 6)
8. Day 7-8: fixes merge continuously as found
9. `agent/10-integration` owns the final pre-demo stabilization branch, merged last each day

**Rule:** an agent branch should be rebased onto `main` at the start of each work session (not merged backward mid-task) to minimize drift, since contracts rarely change once frozen.

## 4. Merge Conflict Handling

- **Shared files (contracts, data model, `core/`):** these are owned by AGENT_01 for the Day 0 freeze. After Day 0, any change to `04_API_CONTRACTS.md`/`05_DATA_MODEL.md`/`app/core` requires: (a) a Contract Changelog entry, (b) explicit notification (a message/commit tag `[CONTRACT-CHANGE]`) so every affected agent rebases before continuing.
- **Non-shared files:** since each agent owns a distinct directory (`03_COMPONENT_ARCHITECTURE.md` §3.13 ownership table), true merge conflicts should be rare. If two agents touch the same file (e.g., a shared router file in `app/api`), the later-merging agent resolves by re-running that endpoint's tests, not by blind `git merge` acceptance.
- **Database migration conflicts:** only AGENT_01 (Day 0) and, if a schema change is truly required later, a designated single agent generates migrations — never two agents generating conflicting Alembic revisions in parallel. If a package needs a new column, it requests it via a `[SCHEMA-CHANGE]` note and AGENT_01/AGENT_10 applies it centrally.

## 5. Interface-First Development

Every agent's task file (`AGENT_TASKS/AGENT_0X_*.md`) lists its **exact function signatures / endpoint contracts** before implementation starts. An agent whose work depends on another agent's not-yet-finished package should code against a stub/mock matching the contract (e.g., `commerce_agent` tests against a `FakeGuardianClient` returning canned `APPROVE`/`BLOCK` responses matching the `GuardianDecision` schema) rather than blocking.

## 6. Definition of "Ready to Merge" (per agent, before opening a PR into `main`)

1. All tests listed in the agent's task file pass.
2. Import-graph lint passes.
3. No modification to files outside the agent's owned directories (see `18_DEFINITION_OF_DONE.md` for the enforcement checklist) — if a shared file *must* change, it's called out explicitly and flagged `[CONTRACT-CHANGE]`.
4. Code matches the contract in `04_API_CONTRACTS.md`/`05_DATA_MODEL.md` exactly (field names, types).

## 7. Communication Artifact

Since this is a solo developer directing agents (not a live team), "communication" means: the developer reviews each agent's task file completion against its acceptance criteria before triggering the next dependent agent, and maintains a running `CHANGELOG.md` at repo root logging each merge and any `[CONTRACT-CHANGE]`/`[SCHEMA-CHANGE]` events for their own tracking.

## 8. Parallelization Summary (also see `16_DEVELOPMENT_PLAN_10_DAYS.md`)

Maximum useful parallelism is **3 agents at once** in this architecture (e.g., Day 2: Guardian + Razorpay; Day 5: Frontend + Security) because most packages have a real dependency on Foundation/Catalog/Guardian landing first. Running more than 3 agents truly concurrently on Day 0-1 offers little benefit since almost everything depends on the frozen contracts and seed data.
