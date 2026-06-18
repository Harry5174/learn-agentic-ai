# Runtime Baseline Inventory

## Scope

This inventory records the Artifact 04 runtime structure for A6.0. It is
measurable by line count and intentionally does not refactor any files.

Measured commands:

```bash
find 04-approval-gated-real-github-comment-adapter/src/app -type f -name "*.py" -print0 \
  | xargs -0 wc -l \
  | sort -n

find 04-approval-gated-real-github-comment-adapter/tests -type f -name "*.py" -print0 \
  | xargs -0 wc -l \
  | sort -n
```

## Top-Level Totals

- `src/app`: 9,839 Python lines
- `tests`: 13,107 Python lines

## Module Totals

| Module | Lines | Files | Purpose | Future A6 relevance |
|--------|------:|------:|---------|---------------------|
| `tools` | 1,864 | 10 | Controlled tool execution, fake/durable/real GitHub comment paths, result schemas | Future operator actions must not merge UI/API review logic into tool execution |
| `skill_graph` | 1,404 | 9 | Skill-run graph, approval pause/resume, execution context, routing | Future operator API will read/act on approval state through service boundaries |
| `github` | 1,326 | 10 | Fake client, real client, real-mode config, token provider, remote marker/reconciliation | Keep token and network boundaries server-owned; do not expose through operator API |
| `skills` | 1,099 | 6 | Skill registry, schemas, argument validation | Future operator views may display trusted skill metadata |
| `side_effects` | 1,069 | 8 | Durable ledger, approval binding, side-effect schemas, idempotency | Primary future operator approval/action integration point |
| `api` | 1,052 | 9 | Existing FastAPI routes, schemas, dependencies, rate limits | Pattern for future thin `operator_routes.py`, not a dumping ground |
| `graph` | 721 | 6 | Inherited task graph used by task routes | Not a future operator API target |
| `audit` | 574 | 5 | Audit schemas, logger, durable audit store | Future operator audit views should read from this boundary |
| `proposer` | 408 | 6 | Fake proposer, optional mocked LLM boundary | Operator API must not trust proposer output |
| `policy` | 96 | 3 | Deterministic policy guard | Future operator actions must preserve policy checks |
| `identity` | 87 | 5 | Server-derived demo identity resolver and schemas | Future operator API must derive actor identity here |
| `persistence` | 86 | 2 | SQLite connection manager | Shared persistence utility for durable stores |
| `approval` | 35 | 2 | Approval request/decision schemas | Future API will likely reuse or extend approval contracts |
| `state` | 16 | 2 | Task status schemas | Low direct A6 relevance |

## Watchlist Files

| File | Lines | Status | A6 guidance |
|------|------:|--------|-------------|
| `src/app/tools/github_comment_real_execution.py` | 754 | Watchlist / future refactor candidate | Real-mode execution boundary. Do not modify in A6.0. Future changes need focused tests and explicit scope approval. |
| `src/app/skill_graph/graph.py` | 704 | Watchlist / future refactor candidate | Approval graph integration point. Do not absorb operator API or UI concerns here. |
| `src/app/tools/github_comment_durable_execution.py` | 520 | Watchlist / future refactor candidate | Durable side-effect execution boundary. Keep approval/hash enforcement here, but do not add inbox/UI logic. |
| `src/app/api/skill_routes.py` | 374 | Healthy pattern / size watch | Existing route pattern for skill runs. Future operator routes should be separate and thin. |
| `src/app/github/real_client.py` | 348 | Security-sensitive healthy boundary | Real GitHub client and token boundary. Do not expose to operator request bodies. |

## Candidate Integration Points

- `src/app/side_effects/approval_binding.py`: approve/reject binding lifecycle
- `src/app/side_effects/durable_ledger.py`: side-effect status and evidence
- `src/app/audit/durable_store.py`: durable audit event retrieval
- `src/app/skill_graph/service.py`: existing paused-run service pattern
- `src/app/api/skill_routes.py`: existing thin-route pattern

## Do-Not-Touch Boundaries For A6.0

A6.0 must not modify Artifact 04 runtime files. It must not copy runtime code,
add operator routes, add UI, or refactor the watchlist files.
