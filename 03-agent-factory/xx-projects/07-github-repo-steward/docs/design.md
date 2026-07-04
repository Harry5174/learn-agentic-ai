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

## 13. Sprint 7.2 Deterministic Analyzer

Sprint 7.2 adds the next local-only runtime slice:

```text
Local JSON fixture snapshot
        ↓
Fixture loader
        ↓
Normalizer
        ↓
Deterministic analyzer
        ↓
Structured findings
```

The analyzer consumes `NormalizedRepoSnapshot` and returns `RepoFinding`
records. Findings are observations about local fixture state, not proposals and
not executable actions. They have stable IDs, stable ordering, severity, target
metadata, summaries, and evidence strings.

Sprint 7.2 implements deterministic rules for:

- open issues labeled `needs-info`
- stale open issues with no comments
- open pull requests with failing CI
- open pull requests waiting for review

The analyzer does not read the current date, environment variables, `.env`,
network resources, GitHub APIs, or LLM providers. It does not mutate the
normalized snapshot and does not create proposal objects, comments, labels,
approval records, ledger entries, or executor commands.

This finding boundary prepares future proposal-provider work by giving that
future layer structured local observations to consume. Future proposals must be
implemented in a separate sprint and treated as untrusted input until policy,
approval, ledger, and execution boundaries exist.

## 14. Sprint 7.3 Proposal Model and Fake Provider Boundary

Sprint 7.3 adds the next local-only runtime slice:

```text
Local JSON fixture snapshot
        ↓
Fixture loader
        ↓
Normalizer
        ↓
Deterministic analyzer
        ↓
Structured findings
        ↓
Fake proposal provider
        ↓
Non-executing fake proposal drafts
```

Findings are observations about local fixture state. Fake proposal drafts are
structured, non-executing proposal objects derived from those findings. A draft
may contain a suggested comment body and rationale, but it does not represent a
posted comment, a policy decision, an approval decision, a ledger record, or an
executor command.

The Sprint 7.3 fake provider is deterministic and local. It uses template text
and standard-library code only; it does not call a real LLM provider, GitHub
API, network resource, environment variable, or `.env` file. It is a stand-in
for a future provider implementation behind the same proposal boundary, not
evidence that real LLM proposal generation exists.

Every Sprint 7.3 proposal object is a draft, has `requires_approval=True`, and
has `execution_status="draft_only"`. This means a future policy and approval
path would be required before any future execution path could exist. It does
not mean any approval inbox, approval decision, ledger entry, or executor is
implemented in this sprint.

Sprint 7.3 prepares future policy guard work by giving that future layer a
small structured proposal shape to validate. It prepares future approval inbox
work by explicitly marking every draft as requiring future approval. It does
not implement either layer.

## 15. Sprint 7.4 Proposal Safety / Policy Guard

Sprint 7.4 adds the next local-only runtime slice:

```text
Local JSON fixture snapshot
        ↓
Fixture loader
        ↓
Normalizer
        ↓
Deterministic analyzer
        ↓
Structured findings
        ↓
Fake proposal provider
        ↓
Non-executing fake proposal drafts
        ↓
Local policy guard
        ↓
Structured policy evaluations
```

The policy guard consumes `RepoProposal` objects and returns
`ProposalPolicyEvaluation` records. Each evaluation has a stable ID, a policy
verdict, reasons when blocked, the proposal risk level, and explicit flags that
future operator approval is still required.

The `allowed_for_operator_review` verdict means only that a draft passed the
Sprint 7.4 local policy checks and may be routed to a future operator-review
layer. It is not approval, it does not make a proposal executable, and it does
not record a decision. Every policy evaluation still has
`requires_operator_approval=True`.

The `blocked_by_policy` verdict means the local guard found an unsafe or
unsupported draft. Blocked evaluations include reasons and are not safe for
future operator review.

Policy evaluation differs from approval because it is deterministic local
screening performed by the harness before any future human decision. Approval
would require a future operator-review layer, an explicit operator identity,
and a recorded decision. Sprint 7.4 implements none of that.

Policy evaluation differs from execution because it never mutates a repository,
never writes a ledger entry, never enqueues approval work, never calls GitHub,
and never invokes a dry-run or real executor. It only evaluates local proposal
objects.

Sprint 7.4 also preserves the fixture boundary from Sprint 7.1: the committed
`fake_repo_snapshot.json` is a canonical internal fixture shape, not a raw
GitHub REST API payload. Future real GitHub read support must pass through a
dedicated adapter sprint that maps raw endpoint payloads into this internal
model before analyzer, proposal, policy, approval, ledger, or executor layers
consume the data.

This sprint prepares a future approval inbox by producing structured local
policy results that can later be routed for operator review. It does not
implement the approval inbox itself.

## 16. Sprint 7.5 Approval Inbox Integration

Sprint 7.5 adds the next local-only runtime slice:

```text
Local JSON fixture snapshot
        ↓
Fixture loader
        ↓
Normalizer
        ↓
Deterministic analyzer
        ↓
Structured findings
        ↓
Fake proposal provider
        ↓
Non-executing fake proposal drafts
        ↓
Local policy guard
        ↓
Structured policy evaluations
        ↓
Local approval inbox intake
        ↓
Pending approval inbox items
```

The approval inbox integration consumes `RepoProposal` objects and matching
`ProposalPolicyEvaluation` records. It creates `ApprovalInboxItem` records only
for evaluations with `allowed_for_operator_review`. Blocked policy evaluations
do not enter the inbox.

An inbox item with `status="pending_operator_review"` means only that a draft
is waiting for a future operator decision layer. It is not approval, rejection,
execution, audit, persistence, or ledger recording. Every inbox item still has
`requires_operator_approval=True`.

Approval inbox intake differs from operator decision handling because Sprint
7.5 does not authenticate an operator, accept approve/reject input, bind a
decision, or record a decision history. It only produces deterministic pending
items from policy-allowed local drafts.

Approval inbox intake differs from execution because it never mutates a
repository, never writes a ledger entry, never calls GitHub, and never invokes
a dry-run or real executor. It only builds local pending-review records.

Sprint 7.5 still preserves the fixture boundary from Sprint 7.1:
`fake_repo_snapshot.json` is a canonical internal fixture shape, not a raw
GitHub REST API payload. A future GitHub API adapter sprint remains required
before any real GitHub read/write claim.

This sprint prepares future operator decision handling by establishing stable
pending inbox item IDs, deterministic inbox order, and explicit linkage back to
proposal and policy evaluation records. It does not implement operator
decision handling itself.

## 17. Sprint 7.6 Operator Decision Handling

Sprint 7.6 adds the next local-only runtime slice:

```text
Local JSON fixture snapshot
        ↓
Fixture loader
        ↓
Normalizer
        ↓
Deterministic analyzer
        ↓
Structured findings
        ↓
Fake proposal provider
        ↓
Non-executing fake proposal drafts
        ↓
Local policy guard
        ↓
Structured policy evaluations
        ↓
Local approval inbox intake
        ↓
Pending approval inbox items
        ↓
Local operator decision records
```

The operator decision layer consumes `ApprovalInboxItem` objects and returns
`OperatorDecisionRecord` records. A decision may be
`approved_by_operator` or `rejected_by_operator`. Every decision record has
`status="local_decision_recorded"`,
`execution_status="not_executed"`, and
`ledger_status="not_recorded"`.

Operator decision handling differs from execution because it never mutates a
repository, never posts a comment, never applies a label, never closes an
issue, never changes a pull request, never calls GitHub, and never invokes a
dry-run or real executor. `approved_by_operator` means only that the operator
recorded local approval for a pending inbox item. It is not a GitHub write and
does not make a proposal executable in Sprint 7.6.

Operator decision handling differs from ledger/audit runtime because it does
not persist audit events, allocate ledger entry IDs, reconcile replay, or bind
execution evidence. `rejected_by_operator` means only that the operator
recorded local rejection for a pending inbox item. It is not a ledgered
rejection and does not prove durable audit storage.

Sprint 7.6 keeps the rejected-decision rationale requirement local and
deterministic. Rejections without a rationale fail safely. Invalid decision
values, missing operator identity, duplicate decisions for one inbox item, and
decisions for unknown inbox items also fail safely.

The decision ID format is deterministic:

```text
a7d:{inbox_item_id}:{decision}
```

Batch decision output is sorted by the same target-oriented order used by the
approval inbox. This keeps decision order stable even if inbox items or input
decision dictionaries are supplied in a different order.

Sprint 7.6 still preserves the fixture boundary from Sprint 7.1:
`fake_repo_snapshot.json` is a canonical internal fixture shape, not a raw
GitHub REST API payload. A future GitHub API adapter sprint remains required
before raw endpoint payloads may feed analyzer, proposal, policy, approval,
decision, ledger, or executor layers.

This sprint prepares future ledger/audit integration by producing structured
local decision records that a later sprint can consume. It deliberately does
not implement that ledger/audit integration.

## 18. Non-Goals

- Full GitHub Repo Steward runtime.
- Real GitHub reads.
- Real GitHub writes.
- GitHub API adapter implementation.
- Real issue comments.
- Label mutation.
- Issue closing.
- Pull request mutation.
- Branch or commit creation.
- Workflow dispatch.
- Required real LLM calls.
- Ledger runtime.
- Dry-run executor runtime.
- Ledger/audit runtime.
- Executor or dry-run executor runtime.
- Background automation.
- Production deployment.

## 19. Future Sprint Candidates

- A7.7 local ledger/audit evidence.
- A7.8 dry-run executor.
- A7.x optional real-mode design review, only after explicit approval.
