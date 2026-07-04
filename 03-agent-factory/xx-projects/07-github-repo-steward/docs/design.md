# Artifact 07 Design Outline

## 1. Current Status After Sprint 7.6

Artifact 07 is a local/fake GitHub Repo Steward vertical-agent scaffold. After
Sprint 7.6, the implemented local layers are:

```text
canonical fixture snapshot
normalizer
deterministic analyzer
fake proposal provider
policy guard
approval inbox
operator decision records
```

These layers operate on committed local fixture data and deterministic in-memory
records. They do not read GitHub, call GitHub APIs, call a real LLM provider,
write ledger/audit records, run an executor, or perform repository mutation.

Sprint 7.6R is a documentation and roadmap revision sprint only. It updates the
formal design outline to match the implementation path through Sprint 7.6 and
to make the remaining safety gates explicit before future ledger, executor, and
real GitHub work.

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
| 7.6R | Formal Design Outline Revision and Roadmap Alignment | current | Documentation-only alignment of design, roadmap, safety boundaries, and evidence interpretation. |

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
Future Ledger / Audit Record
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

Future, unimplemented layers:

- ledger/audit runtime
- dry-run executor
- executor runtime
- GitHub API read adapter
- real-read evidence gate
- real-write readiness gate

## 4. Current Runtime Capability Boundary

The current runtime can load a committed local fixture snapshot, normalize it,
derive deterministic findings, create fake proposal drafts, evaluate those
drafts with local policy rules, build pending approval inbox items, and record
local operator approve/reject decision records.

The current runtime cannot:

- persist ledger/audit records
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
status executes, writes ledger/audit entries, calls GitHub, or proves a future
side effect is safe.

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
| 7.6R | Formal Design Outline Revision and Roadmap Alignment | current |
| 7.7 | Local Ledger / Audit Record Integration | future |
| 7.8 | Dry-Run Executor | future |
| 7.9 | GitHub API Read Adapter Contract | future |
| 7.10 | Real-Read Mode Evidence Gate | future |
| 7.11 | Real-Write Readiness Gate | future |
| 7.12 | Artifact 07 Closeout and AFDF Framework Update | future |

## 8. Three-Role Evidence Lifecycle

Future Artifact 07 sprints must follow the three-role evidence lifecycle:

1. IDE Agent produces an evidence report with raw command outputs.
2. Implementation Supervisor derives a completion report and recommendation
   from that evidence.
3. Design Supervisor issues the final green gate, closeout decision, and next
   sprint authorization.

The IDE Agent must not issue the final green gate. The Implementation
Supervisor must not self-close the sprint. The Implementation Supervisor may
recommend only `GREEN CANDIDATE`, `AMBER CANDIDATE`, or `RED / BLOCKED`.

## 9. Safety Invariants Before Ledger/Executor Work

Before ledger or executor work begins:

- fake/default mode remains first
- real mode remains explicit only
- no `.env` is read or pasted
- no secrets are printed
- no live external side effect occurs without Product Owner approval
- approval must precede any future side effect
- operator decisions remain local records until ledger/audit runtime exists
- ledger/audit evidence must exist before any completion claim involving
  execution or persistence
- executor work must start as dry-run only
- LLM proposes; harness decides; operator approves

## 10. Safety Invariants Before Real GitHub Work

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

## 11. Non-Claims / Overclaim Prevention

Sprint 7.6R does not claim:

- Artifact 07 is complete
- Artifact 07 is production-ready
- ledger/audit runtime exists
- dry-run executor exists
- executor runtime exists
- GitHub API adapter exists
- real GitHub reads are safe
- real GitHub writes are safe
- real GitHub integration exists
- real LLM integration exists

The only Sprint 7.6R completion claim is that the formal design outline,
roadmap, safety-boundary documentation, evidence interpretation, and project
index wording have been revised when validation evidence supports that claim.
