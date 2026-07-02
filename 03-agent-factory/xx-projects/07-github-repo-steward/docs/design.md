# Artifact 07 Design Scaffold

## 1. Problem Statement

The Agent Factory sequence has proven controlled local/demo side effects,
release-gated real GitHub issue-comment evidence, and an operator approval
workbench. The next vertical-agent step needs a GitHub Repo Steward that can
reason over repository state and propose useful maintenance actions without
turning model output into autonomous repository mutation.

Sprint 7.0 documents the intended shape before implementation begins.

## 2. Artifact 07 Thesis

Artifact 07 should demonstrate a proposal-first repository stewardship agent:

```text
LLM proposes.
Harness decides.
Operator approves.
Executor acts only after approval.
```

The model or proposal provider may suggest actions, but the harness owns
normalization, validation, policy, approval routing, execution mode, ledger
state, and audit evidence.

## 3. Intended User/Operator Flow

1. A local fixture repo snapshot is loaded.
2. The repo intake layer normalizes issues, repository metadata, and candidate
   stewardship context.
3. A repo steward analyzer identifies deterministic observations and risks.
4. A fake proposal provider suggests candidate stewardship actions.
5. A safety and policy guard accepts, rejects, or requires approval for each
   proposal.
6. Approval-required proposals enter an approval inbox.
7. The operator approves or rejects with evidence visible.
8. Approved proposals are recorded in a ledger/audit trail.
9. The executor runs in dry-run mode by default and records what would happen.

## 4. Proposed Future Architecture

```text
Fixture Repo Snapshot
        ↓
Repo Intake / Normalizer
        ↓
Repo Steward Analyzer
        ↓
Proposal Provider
        ↓
Safety / Policy Guard
        ↓
Approval Inbox
        ↓
Operator Decision
        ↓
Ledger / Audit Evidence
        ↓
Dry-run Executor by default
```

This is an architecture target for future sprints, not implemented runtime in
Sprint 7.0.

## 5. Key Boundaries

- Fixture/local input before any live repository input.
- Fake proposal provider before any real LLM provider.
- Dry-run executor before any real external side effect.
- Policy guard before approval inbox.
- Operator decision before execution.
- Ledger/audit evidence before any completion claim.

## 6. Proposal-First Model

The proposal provider produces candidate actions. It does not execute them,
authorize them, mutate repositories, or bypass policy. Proposals should be
treated as untrusted input until normalized, validated, policy-checked, and
approved when needed.

Initial proposal examples for future sprints may include draft issue triage,
label suggestions, stale-issue recommendations, documentation cleanup
recommendations, or dependency review notes. In Sprint 7.0 these remain design
examples only.

## 7. Approval-Gated Side Effect Model

Any future external side effect must be routed through:

1. validated proposal intent
2. policy decision
3. approval requirement
4. operator approval
5. ledger/audit recording
6. explicit execution mode
7. executor result evidence

Without those controls, the executor must not perform real repository mutation.

## 8. Fake/Default-First GitHub Strategy

Sprint 7.0 adds no GitHub client. Future sprints should start with fixture repo
snapshots and fake GitHub adapters. Real GitHub writes must remain out of the
default path and require separate Product Owner approval before implementation
or execution.

## 9. Fake/Default-First LLM Strategy

Sprint 7.0 adds no real LLM provider requirement. Future sprints should start
with deterministic fake proposal providers so tests can prove policy and
approval behavior without network access, credentials, cost, or nondeterminism.

An optional provider-neutral boundary may be designed later, but no provider
should be required for the default demo.

## 10. Relationship to Previous Artifacts

- Artifact 04 provides the local/demo real GitHub comment adapter boundary and
  shows why real external side effects require explicit gates.
- Artifact 05 packages release-gate evidence and reinforces that live evidence
  must be narrow, redacted, and not overclaimed.
- Artifact 06 provides the operator approval workbench context for reviewing
  proposed actions before execution.
- Artifact 07 should inherit these safety lessons while staying a vertical-agent
  scaffold in Sprint 7.0.

## 11. Sprint 7.0 Deliverables

- Artifact README.
- Design scaffold.
- Safety-boundary contract.
- Evidence README.
- Sprint 7.0 validation summary.
- Tests placeholder and future test plan.
- Root artifact index updates where applicable.

## 12. Sprint 7.1 Fixture Snapshot and Normalizer

Sprint 7.1 adds the first local runtime slice:

```text
Local JSON fixture snapshot
        ↓
Fixture loader
        ↓
Normalizer
        ↓
Typed internal records
```

This slice loads a committed fake GitHub-like repository snapshot from disk and
normalizes repository identity, labels, issues, pull requests, comments, and
CI/status summaries into dataclass records.

The fixture uses fixed timestamps and explicit `stale_days` values so tests are
deterministic and do not depend on the current date. The loader and normalizer
use only the Python standard library and do not read environment variables,
`.env`, network resources, GitHub APIs, or LLM providers.

The normalizer prepares future analyzer work by creating a stable typed input
shape. It does not analyze the repository, infer stewardship actions, generate
proposals, route approvals, write ledger records, or execute anything.

## 13. Non-Goals

- Full GitHub Repo Steward runtime.
- Real GitHub reads.
- Real GitHub writes.
- Real issue comments.
- Label mutation.
- Issue closing.
- Pull request mutation.
- Branch or commit creation.
- Workflow dispatch.
- Required real LLM calls.
- Background automation.
- Production deployment.

## 14. Future Sprint Candidates

- A7.2 deterministic analyzer and fake proposal provider.
- A7.3 policy guard and rejection evidence.
- A7.4 approval inbox and decision binding.
- A7.5 local ledger/audit evidence and dry-run executor.
- A7.x optional real-mode design review, only after explicit approval.
