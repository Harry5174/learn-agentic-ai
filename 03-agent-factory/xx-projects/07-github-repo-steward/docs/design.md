# Artifact 07 Design Outline

## 1. Final Status After Sprint 7.12

Artifact 07 is closed as a completed local/fake-first GitHub Repo Steward
prototype. After Sprint 7.12, the validated local layers are:

```text
raw GitHub-like fixture payloads
GitHub read adapter contract
canonical fixture snapshot
normalizer
deterministic analyzer
fake proposal provider
policy guard
approval inbox
operator decision records
local ledger/audit records
local dry-run execution results
real-read mode evidence gate
real-write readiness gate
```

These layers operate on committed local fixture data and deterministic in-memory
records. They do not read GitHub, call GitHub APIs, call a real LLM provider,
persist ledger/audit records, run a real executor, or perform repository
mutation.

Sprint 7.12 adds closeout evidence and AFDF framework memory updates only. It
does not call GitHub, authenticate, read `.env`, perform writes, add GitHub
SDKs, add SQLite, add files-on-disk persistence, add real executor runtime, or
add real LLM integration.

## 2. Completed Sprint Summary

| Sprint | Name | Status | Narrow Capability Proven |
|--------|------|--------|--------------------------|
| 7.0 | Design Scaffold and Safety Contract | closed | Documentation scaffold, safety contract, evidence locations, and future test plan. |
| 7.1 | Fixture Repo Snapshot and Normalizer | closed | Local fixture loading and typed normalization into internal records. |
| 7.2 | Deterministic Repo Steward Analyzer | closed | Deterministic local stewardship findings from normalized fixture data. |
| 7.3 | Proposal Model and Fake Proposal Provider Boundary | closed | Non-executing fake proposal drafts from deterministic findings. |
| 7.4 | Proposal Safety / Policy Guard | closed | Deterministic local policy evaluations for fake proposal drafts. |
| 7.5 | Approval Inbox Integration | closed | Pending approval inbox items from policy-allowed proposal drafts. |
| 7.6 | Operator Decision Handling | closed | Local approve/reject operator decision records for pending inbox items. |
| 7.6R | Formal Design Outline Revision and Roadmap Alignment | closed | Documentation-only alignment of design, roadmap, safety boundaries, and evidence interpretation. |
| 7.7 | Local Ledger / Audit Record Integration | closed | Local in-memory ledger/audit records for operator decision evidence. |
| 7.8 | Dry-Run Executor | closed | Local dry-run execution result records for ledgered operator decisions. |
| 7.9 | GitHub API Read Adapter Contract | closed | Local raw GitHub-like fixture adapter into canonical internal snapshot shape. |
| 7.10 | Real-Read Mode Evidence Gate | closed | Local gate records for fake/default adapter evidence and blocked/preflight real-read requests. |
| 7.11 | Real-Write Readiness Gate | closed | Local gate records for fake/default write-readiness blocked and blocked/preflight real-write readiness requests. |
| 7.12 | Artifact 07 Closeout and AFDF Framework Update | closed | Documentation, evidence, and AFDF memory reconciliation for final Artifact 07 closeout review. |

Each sprint proves only its own layer. Earlier evidence does not prove later
layers.

## 3. Revised Architecture Diagram

```text
Raw GitHub-like Fixture Payloads
        |
        v
GitHub Read Adapter Contract
        |
        v
Canonical Internal Snapshot
        |
        v
Normalizer
        |
        v
Deterministic Analyzer
        |
        v
Fake Proposal Provider
        |
        v
Policy Guard
        |
        v
Approval Inbox
        |
        v
Operator Decision Record
        |
        v
Ledger / Audit Record
        |
        v
Dry-Run Executor
        |
        v
Real-Read Mode Evidence Gate
        |
        v
Real-Write Readiness Gate
        |
        v
Artifact 07 Closeout Evidence
```

Validated through Sprint 7.12:

- canonical internal fixture snapshot
- local raw GitHub-like fixture adapter contract
- normalizer
- deterministic analyzer
- fake proposal provider
- policy guard
- approval inbox
- local operator decision records
- local ledger/audit records
- local dry-run execution results
- local real-read evidence gate
- local real-write readiness gate

Future, unimplemented layers:

- executor runtime

## 4. Current Runtime Capability Boundary

The local runtime can load committed local raw GitHub-like fixture payloads,
map them into the canonical internal snapshot dictionary shape, normalize that
snapshot, derive deterministic findings, create fake proposal drafts, evaluate
those drafts with local policy rules, build pending approval inbox items, and
record local operator approve/reject decision records with local ledger/audit
evidence records, then convert those audit records into local dry-run execution
results, local real-read evidence records, and local real-write readiness
records.

The local runtime cannot:

- persist ledger/audit records to disk or a database
- run a real executor
- call GitHub APIs
- read live GitHub data
- write live GitHub data
- adapt live raw GitHub API responses
- call a real LLM provider
- prove production readiness

`approved_by_operator` means only that a local decision record exists.
`rejected_by_operator` means only that a local rejection record exists. Neither
status executes, writes durable ledger/audit entries, calls GitHub, or proves a
future side effect is safe.

`LedgerAuditRecord` means only that local audit evidence was structured from a
local operator decision and matching approval inbox context. It is not a
side-effect ledger entry, durable audit event, GitHub write, executor command,
or proof of execution readiness.

`DryRunExecutionResult` means only that a ledgered local operator decision was
converted into a local simulation record. It is not a GitHub write, not a real
executor command, not durable persistence, and not evidence that a future side
effect was safe or performed.

`GitHubReadAdapterResult` means only that local raw GitHub-like fixture payloads
were mapped into canonical internal snapshot-shaped data. It is not a live
GitHub API response, not authentication, not complete GitHub API coverage, and
not evidence that real GitHub reads are safe.

`RealReadGateEvaluation` means only that a local request object was evaluated
against the real-read evidence gate. `fake_default_allowed` keeps the local
adapter path available without credentials. `real_read_blocked` means the gate
denied a real-read request before any GitHub access. `real_read_preflight_allowed`
means only that the request metadata is sufficient for a future explicitly
authorized read-only evidence collection step; it is not proof that a real read
happened, not proof that credentials were inspected, and not write readiness.

`RealReadEvidenceRecord` means only that local gate evidence was structured. In
Sprint 7.10 the evidence records represent either the fake/default adapter path
or a blocked/preflight real-read request. No live GitHub read was authorized or
attempted in this sprint.

## 5. Canonical Fixture vs Raw GitHub API Boundary

The committed `fake_repo_snapshot.json` fixture is a canonical internal fixture
shape. It is not a raw GitHub REST API response mock.

The internal Artifact 07 layers consume normalized internal records, not raw
GitHub endpoint payloads. Future real GitHub read work must introduce a
dedicated adapter boundary:

```text
Raw GitHub API Responses
        |
        v
GitHub API Read Adapter
        |
        v
Canonical Internal Repo Snapshot
        |
        v
Normalizer / Analyzer / Proposal / Policy / Approval layers
```

Raw GitHub API responses must never be fed directly into analyzer, proposal,
policy, approval, ledger, or executor layers.

## 6. Required GitHub API Adapter Gate

Sprint 7.9 provides a local GitHub-like fixture adapter contract before any
real-read or real-write claim. Future real-read work must still prove:

- live raw GitHub endpoint payloads are mapped into the canonical internal
  snapshot shape
- missing or malformed remote data fails safely
- authentication and token handling are not exposed to internal layers
- analyzer/proposal/policy/approval layers continue to consume internal records
- no real write path is introduced by the read adapter itself

The local adapter gate happens after local ledger/audit and dry-run result work,
so future real-read evidence has a safer local record and execution boundary to
attach to. Sprint 7.9 itself still uses committed fixtures only.

## 7. Sprint 7.10 Real-Read Mode Evidence Gate

Sprint 7.10 adds a local evidence gate around optional future real-read mode.
Fake/default remains the default because it requires no credentials, no `.env`,
no network, and no live GitHub provider. A real-read request is blocked unless
it includes explicit Product Owner authorization, a repository target, safe
credential-handling metadata, the Sprint 7.9 adapter boundary, forbidden write
operations, and explicit read-only network preflight intent.

The gate differs from live GitHub integration. It evaluates local request
metadata and returns deterministic records; it does not call GitHub, inspect
credentials, read `.env`, capture live payloads, normalize live responses, or
run executor work. Any future authorized live read must capture raw read-only
payload evidence, pass that payload through the Sprint 7.9 adapter boundary,
then feed only the canonical internal snapshot into the normalizer and later
local layers.

Product Owner authorization is required before live read because credentials,
repository privacy, rate limits, and external API access are outside the
fake/default safety boundary. Credential values must not be printed or read from
`.env` by default; Sprint 7.10 records only credential-handling metadata.

Sprint 7.10 does not prove real GitHub writes, GitHub write safety, production
readiness, live GitHub authentication, or complete GitHub API coverage. It
prepares future real-write readiness work only by making the read side explicit,
gated, evidence-labeled, and adapter-bound.

## 8. Revised Future Sprint Roadmap

Future numbering is provisional until approved by the Design Supervisor, but the
order is intentional: ledger and dry-run executor work happen before GitHub API
adapter and real-mode gates.

| Sprint | Name | Status |
|--------|------|--------|
| 7.0 | Design Scaffold and Safety Contract | closed |
| 7.1 | Fixture Repo Snapshot and Normalizer | closed |
| 7.2 | Deterministic Repo Steward Analyzer | closed |
| 7.3 | Proposal Model and Fake Proposal Provider Boundary | closed |
| 7.4 | Proposal Safety / Policy Guard | closed |
| 7.5 | Approval Inbox Integration | closed |
| 7.6 | Operator Decision Handling | closed |
| 7.6R | Formal Design Outline Revision and Roadmap Alignment | closed |
| 7.7 | Local Ledger / Audit Record Integration | closed |
| 7.8 | Dry-Run Executor | closed |
| 7.9 | GitHub API Read Adapter Contract | closed |
| 7.10 | Real-Read Mode Evidence Gate | closed |
| 7.11 | Real-Write Readiness Gate | closed |
| 7.12 | Artifact 07 Closeout and AFDF Framework Update | closed |

## 9. Sprint 7.7 Local Ledger / Audit Record Integration

Sprint 7.7 adds the next local-only runtime slice:

```text
Canonical Internal Fixture Snapshot
        |
        v
Normalizer
        |
        v
Deterministic Analyzer
        |
        v
Fake Proposal Provider
        |
        v
Policy Guard
        |
        v
Approval Inbox
        |
        v
Operator Decision Record
        |
        v
Local Ledger / Audit Record
```

The local ledger layer consumes `OperatorDecisionRecord` objects and matching
`ApprovalInboxItem` context. It returns `LedgerAuditRecord` objects that
preserve the decision ID, inbox item ID, proposal ID, decision value, operator
identity, decision rationale, optional source snapshot ID, and evidence
references.

Ledger/audit records differ from execution because they do not mutate a
repository, post comments, apply labels, close issues, modify pull requests,
call GitHub, run a dry-run executor, or trigger executor work. Every Sprint 7.7
record has `execution_status="not_executed"`,
`github_status="not_called"`, and `executor_status="not_triggered"`.

Ledger/audit records differ from durable persistence because Sprint 7.7 builds
in-memory structured audit records only. It does not add SQLite, database
persistence, files-on-disk persistence, durable replay, durable audit storage,
or production audit guarantees.

This sprint prepares future dry-run executor work by giving that later layer
stable local audit evidence for operator decisions. The future executor must
still be implemented separately and must not infer execution permission from a
ledger/audit record alone.

Sprint 7.7 preserves the fixture boundary from Sprint 7.1:
`fake_repo_snapshot.json` is a canonical internal fixture shape, not a raw
GitHub REST API payload. A future GitHub API adapter sprint remains required
before any real-read or real-write claim.

## 10. Sprint 7.8 Dry-Run Executor

Sprint 7.8 adds the next local-only runtime slice:

```text
Canonical Internal Fixture Snapshot
        |
        v
Normalizer
        |
        v
Deterministic Analyzer
        |
        v
Fake Proposal Provider
        |
        v
Policy Guard
        |
        v
Approval Inbox
        |
        v
Operator Decision Record
        |
        v
Local Ledger / Audit Record
        |
        v
Local Dry-Run Execution Result
```

The dry-run layer consumes `LedgerAuditRecord` objects and matching
`ApprovalInboxItem` context. It returns `DryRunExecutionResult` objects that
preserve ledger record ID, decision ID, inbox item ID, proposal ID, proposal
type, target type, target number, operator decision, and evidence references.

Dry-run results differ from execution because they do not mutate a repository,
post comments, apply labels, close issues, modify pull requests, call GitHub,
trigger executor work, or enqueue real work. Every Sprint 7.8 result has
`execution_status="not_executed"`, `github_status="not_called"`,
`external_side_effect_status="none"`, and
`ledger_record_status="verified_local_audit_record"`.

Approved ledgered decisions produce `dry_run_completed` results with local
planned-action strings such as `would_prepare_issue_comment` or
`would_prepare_pull_request_comment`. Rejected ledgered decisions produce
`dry_run_skipped` no-op results with
`planned_action="no_op_rejected_by_operator"`.

The dry-run layer preserves upstream evidence but deliberately does not perform
side effects. It prepares future executor-readiness discussions by separating
"what would be prepared" from "what was actually executed." Real execution,
durable persistence, real GitHub reads, real GitHub writes, GitHub API adapter
logic, and real LLM integration remain unimplemented.

Sprint 7.8 preserves the fixture boundary from Sprint 7.1:
`fake_repo_snapshot.json` is a canonical internal fixture shape, not a raw
GitHub REST API payload. A future GitHub API adapter sprint remains required
before any real-read or real-write claim.

## 11. Sprint 7.9 GitHub API Read Adapter Contract

Sprint 7.9 adds the local adapter boundary before the canonical snapshot:

```text
Local Raw GitHub-like Fixture Payloads
        |
        v
GitHub Read Adapter Contract
        |
        v
Canonical Internal Snapshot Dictionary
        |
        v
Normalizer
        |
        v
Existing Local Pipeline
```

The raw GitHub-like fixtures are endpoint-family shaped files for repository
identity, labels, issues, pulls, issue comments, pull reviews, check runs, and
statuses. They deliberately differ from `fake_repo_snapshot.json`, which is the
canonical internal fixture shape. For example, an issue-like payload may contain
a `pull_request` marker and must not become a canonical issue.

The adapter maps local raw-like payload dictionaries into the canonical
top-level snapshot fields consumed by `normalize_repo_snapshot`: `repository`,
`labels`, `issues`, `pull_requests`, `comments`, and `ci_statuses`. It derives
canonical pull request review and CI summaries from the local review, check-run,
and status fixtures.

The adapter boundary exists so raw endpoint-shaped payloads never flow directly
into analyzer, proposal, policy, approval, operator-decision, ledger, or
dry-run layers. Those internal layers continue to consume normalized internal
records, with the normalizer remaining the transition point from canonical
snapshot dictionaries to typed records.

Sprint 7.9 does not prove real GitHub reads or writes. It does not add GitHub
authentication, GitHub SDKs, live network calls, real executor runtime, durable
persistence, or real LLM integration. It prepares a future real-read evidence
gate by proving the local mapping contract and failure behavior before any live
GitHub payloads are introduced.

## 12. Three-Role Evidence Lifecycle

Future Artifact 07 sprints must follow the three-role evidence lifecycle:

1. IDE Agent produces an evidence report with raw command outputs.
2. Implementation Supervisor derives a completion report and recommendation
   from that evidence.
3. Design Supervisor issues the final green gate, closeout decision, and next
   sprint authorization.

The IDE Agent must not issue the final green gate. The Implementation
Supervisor must not self-close the sprint. The Implementation Supervisor may
recommend only `GREEN CANDIDATE`, `AMBER CANDIDATE`, or `RED / BLOCKED`.

## 13. Safety Invariants Before Executor Work

Before executor work begins:

- fake/default mode remains first
- real mode remains explicit only
- no `.env` is read or pasted
- no secrets are printed
- no live external side effect occurs without Product Owner approval
- approval must precede any future side effect
- operator decisions and ledger/audit records remain local records
- local ledger/audit evidence must exist before any future completion claim
  involving decisions
- executor readiness work must start from dry-run result evidence
- LLM proposes; harness decides; operator approves

## 14. Safety Invariants Before Real GitHub Work

Before real GitHub read or write work begins:

- a dedicated GitHub API read adapter gate must exist
- raw GitHub API responses must pass through the adapter before internal layers
  consume them
- the canonical internal snapshot boundary must remain stable
- real read mode must be explicit and evidence-gated
- real write execution must remain future until a separate artifact authorizes it
- no GitHub token may be printed, committed, or supplied by client input
- no real GitHub writes may occur without Product Owner approval and operator
  approval
- real GitHub behavior must not be inferred from fixture, fake, or mocked
  evidence

## 15. Non-Claims / Overclaim Prevention

Artifact 07 closeout does not claim:

- Artifact 07 is production-ready
- Artifact 07 is an operational live steward
- durable ledger/audit persistence exists
- executor runtime exists beyond local dry-run result generation
- live GitHub API integration exists
- GitHub authentication exists
- real GitHub reads are safe
- real GitHub writes are safe
- real GitHub integration exists
- real LLM integration exists

The only Sprint 7.12 completion claim is that Artifact 07 is closed as a
local/fake-first GitHub Repo Steward prototype when validation evidence supports
that claim.

## 16. Sprint 7.11 Real-Write Readiness Gate

Sprint 7.11 adds a deterministic local evidence gate around future real-write
readiness.

### What Sprint 7.11 adds

- `RealWriteReadinessRequest`, `RealWriteReadinessEvaluation`, and
  `RealWriteReadinessEvidenceRecord` dataclass models.
- `RealWriteReadinessError` for malformed gate inputs.
- `evaluate_real_write_readiness()` function that evaluates local request
  metadata and returns deterministic records.
- `build_real_write_readiness_evidence_record()` function for structured
  evidence.
- `evaluate_fake_default_real_write_readiness_gate()` convenience helper.

### How real-write readiness differs from real-write execution

Real-write readiness is a metadata-only local gate. It evaluates whether all
upstream evidence identifiers and safety confirmations are present, and whether
the request structure is consistent. It does not call GitHub, authenticate,
read `.env`, perform writes, create side effects, or trigger executor runtime.

Real-write execution would be a separate future layer that consumes the
readiness verdict and actually posts to GitHub APIs. Sprint 7.11 does not
implement any part of real-write execution.

### Why fake/default remains the default

Fake/default mode requires no credentials, network, or external access. It
blocks real-write readiness evaluation automatically, ensuring the safe local
path is the default.

### Why Product Owner authorization is required

Write-readiness preflight involves evaluating metadata about a future write
path that could eventually touch repository state. Product Owner authorization
is required before even the preflight metadata evaluation to prevent accidental
escalation.

### Why credentials must not be printed or read from .env

The gate evaluates local request metadata only. Credential values are never
inspected, printed, or loaded. Future real-write execution would need separate
credential-handling infrastructure, but Sprint 7.11 does not implement it.

### Why real-read evidence must exist before write-readiness

Write-readiness depends on read-gate evidence because real-write proposals
must originate from analyzed repository state. Without verified read evidence,
write-readiness cannot be structurally validated.

### Why dry-run and ledger evidence must exist before write-readiness

Write-readiness requires that the proposal has passed through the complete
local pipeline: policy evaluation, approval inbox, operator decision, ledger
audit, and dry-run simulation. These upstream records must exist before the
gate can confirm readiness.

### Why the gate does not prove real GitHub writes

The gate evaluates local metadata only. It does not call GitHub APIs, does not
authenticate, does not post comments, does not apply labels, does not close
issues, and does not merge pull requests. `real_write_preflight_allowed` means
only that local metadata is structurally consistent for a future review.

### Why the gate does not prove production readiness

Production readiness would require live GitHub integration, real executor
runtime, real authentication, rate-limit handling, error recovery, and
operational monitoring. None of these exist in Sprint 7.11.

### What remains deliberately not implemented

- Real GitHub write execution
- GitHub write API calls
- GitHub authentication for writes
- Real executor runtime
- Real LLM integration
- Durable persistence
- Database or file write evidence
- Write types beyond future comments (no labels, closes, merges, etc.)

### How this prepares future work

Sprint 7.11 establishes the readiness-gate boundary so that future
separate real-write work can reference structured readiness evidence. The gate
pattern mirrors Sprint 7.10's read-gate pattern, keeping the architecture
symmetric.

## 17. Sprint 7.12 Final Closeout

Sprint 7.12 closes Artifact 07 as a local/fake-first GitHub Repo Steward
prototype. It reconciles the artifact README, design, safety boundaries,
evidence index, tests index, parent project README, and AFDF project memory
against the validated Sprint 7.0 through Sprint 7.11 evidence chain.

Final architecture:

```text
Canonical Internal Fixture / GitHub-like Local Fixture
        |
        v
Normalizer
        |
        v
Analyzer
        |
        v
Fake Proposal Provider
        |
        v
Policy Guard
        |
        v
Approval Inbox
        |
        v
Operator Decision
        |
        v
Ledger / Audit Record
        |
        v
Dry-Run Executor Result
        |
        v
GitHub Read Adapter Boundary
        |
        v
Real-Read Evidence Gate
        |
        v
Real-Write Readiness Gate
```

Adapter boundary:

```text
Raw GitHub-like or future real GitHub API payload
        |
        v
GitHub Read Adapter Boundary
        |
        v
Canonical Internal Snapshot
        |
        v
Normalizer and internal Artifact 07 layers
```

Layer responsibilities:

- Fixture and adapter layers provide local canonical snapshot inputs and keep
  raw GitHub-shaped payloads out of internal layers.
- Normalizer, analyzer, fake proposal provider, policy guard, approval inbox,
  operator decision, ledger/audit, and dry-run layers provide deterministic
  local records only.
- Real-read and real-write readiness gates evaluate metadata and evidence
  boundaries only; they do not read, write, authenticate, or execute.
- Closeout evidence records what the local/fake-first chain proves and what it
  deliberately does not prove.

Safety boundaries:

- No real GitHub reads or writes are implemented by Artifact 07.
- No GitHub write APIs, authentication, `.env` reads, secret printing, real
  executor runtime, real LLM provider, durable persistence, or production
  readiness claims are added.
- Real-read evidence does not imply write readiness.
- Real-write readiness does not imply write execution.

What remains future:

- Product Owner selection of the next artifact.
- Any live GitHub read evidence, live GitHub write execution, real executor
  runtime, real LLM integration, durable persistence, authentication, or
  production deployment.

Artifact 07 should close here because it has completed the planned
local/fake-first evidence chain and the next meaningful work would require a
new artifact authorization boundary rather than additional local closeout work.
