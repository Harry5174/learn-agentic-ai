# Artifact 07 Design Outline

## 1. Current Status After Sprint 7.7

Artifact 07 is a local/fake GitHub Repo Steward vertical-agent scaffold. After
Sprint 7.7, the implemented local layers are:

```text
canonical fixture snapshot
normalizer
deterministic analyzer
fake proposal provider
policy guard
approval inbox
operator decision records
local ledger/audit records
```

These layers operate on committed local fixture data and deterministic in-memory
records. They do not read GitHub, call GitHub APIs, call a real LLM provider,
persist ledger/audit records, run an executor, or perform repository mutation.

Sprint 7.7 adds local ledger/audit record integration for operator decision
evidence only. It records structured local audit records in memory; it does not
add SQLite, files-on-disk persistence, durable storage, executor runtime,
dry-run executor runtime, GitHub calls, or real LLM integration.

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
| 7.7 | Local Ledger / Audit Record Integration | current | Local in-memory ledger/audit records for operator decision evidence. |

Each sprint proves only its own layer. Earlier evidence does not prove later
layers.

## 3. Revised Architecture Diagram

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
Ledger / Audit Record
        |
        v
Future Dry-Run Executor
        |
        v
Future GitHub API Read Adapter Contract
        |
        v
Future Real-Read Evidence Gate
        |
        v
Future Real-Write Readiness Gate
```

Implemented through Sprint 7.6:

- canonical internal fixture snapshot
- normalizer
- deterministic analyzer
- fake proposal provider
- policy guard
- approval inbox
- local operator decision records
- local ledger/audit records

Future, unimplemented layers:

- dry-run executor
- executor runtime
- GitHub API read adapter
- real-read evidence gate
- real-write readiness gate

## 4. Current Runtime Capability Boundary

The current runtime can load a committed local fixture snapshot, normalize it,
derive deterministic findings, create fake proposal drafts, evaluate those
drafts with local policy rules, build pending approval inbox items, and record
local operator approve/reject decision records with local ledger/audit evidence
records.

The current runtime cannot:

- persist ledger/audit records to disk or a database
- run a dry-run executor
- run any executor
- call GitHub APIs
- read live GitHub data
- write live GitHub data
- adapt raw GitHub API responses
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

A future GitHub API adapter sprint must be completed before any real-read or
real-write claim. That adapter must prove:

- raw GitHub endpoint payloads are mapped into the canonical internal snapshot
  shape
- missing or malformed remote data fails safely
- authentication and token handling are not exposed to internal layers
- analyzer/proposal/policy/approval layers continue to consume internal records
- no real write path is introduced by the read adapter itself

The adapter gate must happen after local ledger/audit and dry-run executor
work, so future real-read evidence has a safer local record and execution
boundary to attach to.

## 7. Revised Future Sprint Roadmap

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
| 7.7 | Local Ledger / Audit Record Integration | current |
| 7.8 | Dry-Run Executor | future |
| 7.9 | GitHub API Read Adapter Contract | future |
| 7.10 | Real-Read Mode Evidence Gate | future |
| 7.11 | Real-Write Readiness Gate | future |
| 7.12 | Artifact 07 Closeout and AFDF Framework Update | future |

## 8. Sprint 7.7 Local Ledger / Audit Record Integration

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

## 9. Three-Role Evidence Lifecycle

Future Artifact 07 sprints must follow the three-role evidence lifecycle:

1. IDE Agent produces an evidence report with raw command outputs.
2. Implementation Supervisor derives a completion report and recommendation
   from that evidence.
3. Design Supervisor issues the final green gate, closeout decision, and next
   sprint authorization.

The IDE Agent must not issue the final green gate. The Implementation
Supervisor must not self-close the sprint. The Implementation Supervisor may
recommend only `GREEN CANDIDATE`, `AMBER CANDIDATE`, or `RED / BLOCKED`.

## 10. Safety Invariants Before Executor Work

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
- executor work must start as dry-run only
- LLM proposes; harness decides; operator approves

## 11. Safety Invariants Before Real GitHub Work

Before real GitHub read or write work begins:

- a dedicated GitHub API read adapter gate must exist
- raw GitHub API responses must pass through the adapter before internal layers
  consume them
- the canonical internal snapshot boundary must remain stable
- real read mode must be explicit and evidence-gated
- real write mode must remain future until a separate readiness gate
- no GitHub token may be printed, committed, or supplied by client input
- no real GitHub writes may occur without Product Owner approval and operator
  approval
- real GitHub behavior must not be inferred from fixture, fake, or mocked
  evidence

## 12. Non-Claims / Overclaim Prevention

Sprint 7.7 does not claim:

- Artifact 07 is complete
- Artifact 07 is production-ready
- durable ledger/audit persistence exists
- dry-run executor exists
- executor runtime exists
- GitHub API adapter exists
- real GitHub reads are safe
- real GitHub writes are safe
- real GitHub integration exists
- real LLM integration exists

The only Sprint 7.7 completion claim is that local operator decision records can
be converted into deterministic local ledger/audit records when validation
evidence supports that claim.
