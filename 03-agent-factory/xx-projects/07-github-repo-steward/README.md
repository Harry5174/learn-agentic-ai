# Artifact 07 - GitHub Repo Steward

Artifact 07 is a GitHub Repo Steward vertical agent scaffold.

## Artifact Status

Current status after Sprint 7.11:

- local fixture intake
- normalization
- deterministic observational findings
- non-executing fake proposal drafts
- deterministic local policy evaluation
- pending approval inbox items
- local operator decision records
- local ledger/audit records
- local dry-run execution results
- local GitHub-like fixture adapter contract
- local real-read mode evidence gate
- local real-write readiness gate

Artifact 07 is not a completed steward agent.

Still not implemented:

- executor runtime
- real GitHub integration
- live GitHub read behavior
- real GitHub writes
- real LLM integration
- production readiness

## Sprint Status

Sprint 7.0: closed — documentation scaffold and safety contract.

Sprint 7.1: closed — local fixture repo snapshot and normalizer.

Sprint 7.2: closed — deterministic repo steward analyzer.

Sprint 7.3: closed — proposal model and fake proposal provider boundary.

Sprint 7.4: closed — proposal safety / policy guard.

Sprint 7.5: closed — approval inbox integration.

Sprint 7.6: closed — operator decision handling.

Sprint 7.6R: closed — formal design outline revision and roadmap alignment.

Sprint 7.7: closed — local ledger / audit record integration.

Sprint 7.8: closed — dry-run executor.

Sprint 7.9: closed — GitHub API read adapter contract.

Sprint 7.10: closed — real-read mode evidence gate.

Sprint 7.11: real-write readiness gate.

Runtime status: local fixture intake, normalization, deterministic findings,
non-executing fake proposals, local policy evaluation, pending approval
inbox items, local operator decision records, local ledger/audit records,
local dry-run execution results, local GitHub-like fixture adapter contract,
real-read evidence gate, and real-write readiness gate only.

## Purpose

Artifact 07 prepares a future vertical agent that can inspect repository state,
propose stewardship actions, route those proposals through policy and approval,
and preserve audit evidence. Sprint 7.10 proves only that deterministic local
fake GitHub-like snapshot can be loaded, normalized, analyzed into structured
observational findings, converted into non-executing fake proposal drafts, and
evaluated by local policy rules, then converted into pending approval inbox
items for future operator review, local operator decision records, local
ledger/audit records, local dry-run execution results, and local raw
GitHub-like fixture adapter output plus local real-read gate evidence.

## What This Artifact Demonstrates

Sprint 7.0 demonstrates:

- a repository-owned design scaffold for a future GitHub Repo Steward agent
- explicit fake/local/dry-run defaults
- safety boundaries inherited from Artifacts 04, 05, and 06
- an evidence plan that separates documentation proof from runtime proof
- a placeholder test plan for future implementation sprints

Sprint 7.1 demonstrates:

- a local JSON fixture snapshot
- typed normalized records for repository identity, labels, issues, pull
  requests, comments, and CI/status summaries
- deterministic stale metadata representation
- safe rejection of malformed fixture data
- tests that do not require network access, GitHub credentials, `.env`, or a
  real LLM provider

Sprint 7.1 does not demonstrate live repository automation, repo analysis,
proposal generation, approval routing, ledger recording, execution, or
model-driven behavior.

Sprint 7.2 demonstrates:

- structured `RepoFinding` records
- deterministic finding IDs
- deterministic finding order
- local rules for issues missing reproduction details
- local rules for stale issues without recorded maintainer response
- local rules for pull requests with failing CI
- local rules for pull requests waiting for review
- analyzer tests that do not require network access, GitHub credentials, `.env`,
  or a real LLM provider

Sprint 7.2 does not demonstrate proposal generation, approval routing, ledger
recording, execution, live repository automation, or model-driven behavior.

Sprint 7.3 demonstrates:

- structured `RepoProposal` records
- a provider-neutral proposal boundary
- a deterministic fake proposal provider
- deterministic proposal IDs and order
- non-executing fake proposal drafts created from analyzer findings
- local shape validation for proposal draft invariants
- tests that do not require network access, GitHub credentials, `.env`, or a
  real LLM provider

Sprint 7.3 does not demonstrate real LLM proposal generation, policy guard
runtime, approval routing, ledger recording, execution, live repository
automation, or model-driven behavior.

Sprint 7.4 demonstrates:

- structured `ProposalPolicyEvaluation` records
- deterministic policy evaluation IDs and order
- local allow/block verdicts for future operator-review routing
- blocked policy results with reasons
- `requires_operator_approval=True` on every policy evaluation
- `safe_for_operator_review=True` only for proposals allowed for future
  operator review
- local guard checks for completed-action claims and token-like strings
- tests that do not require network access, GitHub credentials, `.env`, or a
  real LLM provider

Sprint 7.4 does not demonstrate approval decisions, approval inbox runtime,
ledger recording, execution, dry-run execution, real GitHub reads or writes,
GitHub API adapter correctness, real LLM integration, or production readiness.

Sprint 7.5 demonstrates:

- structured `ApprovalInboxItem` records
- deterministic inbox item IDs and order
- pending inbox items from policy-allowed proposal drafts
- safe exclusion of blocked proposals from inbox intake
- `status="pending_operator_review"` on every inbox item
- `requires_operator_approval=True` on every inbox item
- local failure for inconsistent proposal/evaluation data
- tests that do not require network access, GitHub credentials, `.env`, or a
  real LLM provider

Sprint 7.5 does not demonstrate operator approval decisions, operator rejection
handling, ledger recording, execution, dry-run execution, real GitHub reads or
writes, GitHub API adapter correctness, real LLM integration, or production
readiness.

Sprint 7.6 demonstrates:

- structured `OperatorDecisionRecord` records
- deterministic local decision IDs and order
- local approval decisions for pending approval inbox items
- local rejection decisions for pending approval inbox items
- `status="local_decision_recorded"` on every decision record
- `execution_status="not_executed"` on every decision record
- `ledger_status="not_recorded"` on every decision record
- safe failure for invalid decisions, missing operator identity, rejection
  without rationale, duplicate decisions, and unknown inbox items
- local decision handling without network access, GitHub credentials, `.env`,
  or a real LLM provider

Sprint 7.6 does not demonstrate ledger recording, audit persistence,
approval-gated execution, dry-run execution, real GitHub reads or writes,
GitHub API adapter correctness, real LLM integration, or production readiness.

Sprint 7.7 demonstrates:

- structured `LedgerAuditRecord` records
- deterministic local ledger record IDs and order
- local audit records for approved operator decisions
- local audit records for rejected operator decisions
- preservation of decision, proposal, inbox, operator, rationale, snapshot, and
  evidence-reference context
- `record_type="operator_decision_audit"` on every ledger record
- `record_status="recorded_locally"` on every ledger record
- `execution_status="not_executed"` on every ledger record
- `github_status="not_called"` on every ledger record
- `executor_status="not_triggered"` on every ledger record
- safe failure for mismatched decision/inbox data, duplicate decisions, unknown
  inbox references, and extra evidence-reference keys
- local ledger handling without network access, GitHub credentials, `.env`, file
  persistence, database persistence, or a real LLM provider

Sprint 7.7 does not demonstrate dry-run execution, executor runtime, real
GitHub reads or writes, GitHub API adapter correctness, real LLM integration,
database or file persistence, durable audit storage, or production readiness.

Sprint 7.8 demonstrates:

- structured `DryRunExecutionResult` records
- deterministic dry-run result IDs and order
- local dry-run results for approved ledgered operator decisions
- local dry-run no-op results for rejected ledgered operator decisions
- preservation of ledger, decision, inbox, proposal, policy, and target
  evidence context
- `execution_status="not_executed"` on every dry-run result
- `github_status="not_called"` on every dry-run result
- `external_side_effect_status="none"` on every dry-run result
- `ledger_record_status="verified_local_audit_record"` on every dry-run result
- safe failure for mismatched ledger/inbox data, duplicate ledger records,
  duplicate inbox items, and missing inbox references
- local dry-run handling without network access, GitHub credentials, `.env`,
  file persistence, database persistence, or a real LLM provider

Sprint 7.8 does not demonstrate executor runtime beyond local dry-run result
generation, real execution, real GitHub reads or writes, GitHub API adapter
correctness, real GitHub integration, real LLM integration, durable
persistence, or production readiness.

Sprint 7.9 demonstrates:

- local raw GitHub-like endpoint fixture payloads
- structured `GitHubReadAdapterResult` records
- deterministic mapping from raw GitHub-like fixture payloads into the
  canonical internal snapshot dictionary shape
- separation of issue-like records with `pull_request` markers from canonical
  issues
- pull request endpoint records becoming canonical pull request records
- deterministic mapping of labels, issue comments, pull reviews, check runs,
  and status summaries
- mapped canonical snapshots that normalize successfully
- mapped normalized snapshots that pass through analyzer, fake proposal
  provider, policy guard, approval inbox, operator decision, ledger, and
  dry-run layers
- safe failure for missing repository payloads, missing pull payloads,
  malformed issue payloads, and malformed pull request payloads
- local adapter handling without network access, GitHub credentials, `.env`,
  file persistence, database persistence, or a real LLM provider

Sprint 7.9 does not demonstrate real GitHub reads, real GitHub writes, GitHub
authentication, GitHub App integration, GitHub OAuth integration, complete
GitHub API payload coverage, real GitHub integration, real LLM integration,
real executor runtime, or production readiness.

Sprint 7.10 demonstrates:

- structured `RealReadRequest` records
- structured `RealReadGateEvaluation` records
- structured `RealReadEvidenceRecord` records
- fake/default mode allowed without credentials
- real-read requests blocked without explicit Product Owner authorization
- real-read requests blocked without a repository target
- real-read requests blocked without safe credential-handling metadata
- real-read requests blocked if the Sprint 7.9 adapter boundary is disabled
- real-read requests blocked if write operations are allowed
- a read-only preflight-allowed state that still does not call GitHub
- deterministic evaluation IDs and evidence IDs
- fake/default adapter-path evidence through the full local pipeline
- local gate handling without network access, GitHub credentials, `.env`, file
  persistence, database persistence, or a real LLM provider

Sprint 7.10 does not demonstrate live GitHub reads, live GitHub read safety,
live GitHub authentication behavior, real GitHub writes, GitHub write
readiness, GitHub App integration, GitHub OAuth integration, complete GitHub API
payload coverage, real executor runtime, real LLM integration, or production
readiness.

Sprint 7.11 demonstrates:

- structured `RealWriteReadinessRequest` records
- structured `RealWriteReadinessEvaluation` records
- structured `RealWriteReadinessEvidenceRecord` records
- fake/default write-readiness blocked by default
- write-readiness blocked without Product Owner authorization
- write-readiness blocked without repository, prior evidence IDs, or operator
  approval
- write-readiness blocked for rejected operator decisions
- write-readiness blocked for unsupported write operation types
- write-readiness blocked if adapter, read-gate, dry-run, ledger, policy, or
  approval confirmations are missing
- write-readiness blocked if secret handling is not confirmed
- write-readiness blocked if executor runtime is enabled
- metadata-only `real_write_preflight_allowed` from complete safe request
- preflight allowed does not call GitHub, does not execute, and is not proof of
  a real write
- deterministic evaluation IDs and evidence IDs
- local write-readiness gate handling without network access, GitHub
  credentials, `.env`, file persistence, database persistence, or a real LLM
  provider

Sprint 7.11 does not demonstrate real GitHub writes, GitHub write safety,
GitHub write execution, GitHub App integration, GitHub OAuth integration,
real executor runtime, real LLM integration, or production readiness.

## Default Mode

The default mode is fake/local/dry-run. The artifact does not perform live
GitHub reads or writes. The artifact does not require a real LLM provider.
Real-read mode is blocked unless the Product Owner explicitly authorizes it
with a repository target, read-only credential-handling metadata, and evidence
expectations.

Sprint 7.10 begins from fixture repository snapshots, normalizes them, produces
deterministic findings, converts those findings into non-executing fake proposal
drafts, evaluates those drafts with deterministic local policy rules, and
creates pending approval inbox items, then records local operator approve/reject
decisions, local ledger/audit records, local dry-run execution results, and
local raw GitHub-like fixture adapter output plus local real-read gate evidence
only.

## Safety Model

The safety model preserves this invariant:

```text
LLM proposes.
Harness decides.
Operator approves.
Executor acts only after approval.
```

Any future real external side effect must require explicit operator approval and
evidence. Real mode must remain opt-in, policy-gated, and separately approved by
the Product Owner before it is implemented or exercised.

## Relationship to Artifact 06

Artifact 06 is the local/demo operator approval workbench. Artifact 07 should
reuse the approval and evidence lessons from Artifact 06, but Sprint 7.0 does
not copy its runtime, extend its routes, or add a new operator UI.

Future Artifact 07 sprints may decide whether to copy the Artifact 06 runtime
baseline, reference it as design context, or introduce a narrower scaffold. That
decision is not implemented in Sprint 7.0.

## In Scope for Sprint 7.0

- Create the Artifact 07 documentation scaffold.
- Define the initial architecture and proposal-first flow.
- Define explicit safety boundaries and forbidden actions.
- Define evidence expectations for a documentation-only sprint.
- Add a tests placeholder that names future test coverage without claiming it
  exists.
- Update root artifact indexes where they list current artifacts.

## In Scope for Sprint 7.1

- Load a committed local JSON fixture snapshot.
- Normalize repository identity, issues, pull requests, labels, comments, and
  CI/status summaries into typed records.
- Represent stale metadata using fixed fixture values.
- Reject missing required fixture fields with local validation errors.
- Prove the loader and normalizer do not require common secret environment
  variables.

## In Scope for Sprint 7.2

- Analyze a normalized local fixture snapshot.
- Produce structured `RepoFinding` records.
- Generate deterministic finding IDs and output order.
- Identify local stewardship signals for open issues and pull requests.
- Prove the analyzer does not require common secret environment variables or
  network access.
- Preserve Sprint 7.1 fixture loading and normalization behavior.

## In Scope for Sprint 7.3

- Define structured `RepoProposal` records.
- Define a provider-neutral proposal boundary.
- Convert analyzer findings into deterministic fake proposal drafts.
- Mark every proposal draft as requiring future approval.
- Keep every proposal draft non-executing with `execution_status="draft_only"`.
- Prove the fake provider does not require common secret environment variables
  or network access.
- Preserve Sprint 7.1 fixture loading, Sprint 7.2 analyzer behavior, and all
  existing tests.

## In Scope for Sprint 7.4

- Define structured local policy evaluation records.
- Evaluate `RepoProposal` objects with deterministic local rules.
- Mark safe drafts as `allowed_for_operator_review` only, not approved.
- Block unsafe drafts with explicit reasons.
- Require future operator approval on every evaluation.
- Detect local completed-action claims and token-like draft text.
- Prove policy evaluation does not require common secret environment variables
  or network access.
- Preserve Sprint 7.1 fixture loading, Sprint 7.2 analyzer behavior, Sprint
  7.3 fake proposal behavior, and all existing tests.

## In Scope for Sprint 7.5

- Define structured local approval inbox item records.
- Convert policy-allowed `RepoProposal` drafts into pending inbox items.
- Keep all inbox items in `pending_operator_review`.
- Require future operator approval on every inbox item.
- Safely exclude blocked policy evaluations from the inbox.
- Fail safely for missing, duplicate, extra, or mismatched proposal/evaluation
  data.
- Prove inbox intake does not require common secret environment variables or
  network access.
- Preserve Sprint 7.1 fixture loading, Sprint 7.2 analyzer behavior, Sprint
  7.3 fake proposal behavior, Sprint 7.4 policy behavior, and all existing
  tests.

## In Scope for Sprint 7.6

- Define structured local operator decision records.
- Record local approve/reject decisions for pending approval inbox items.
- Keep all decision records in `local_decision_recorded`.
- Keep all approved and rejected decisions `not_executed`.
- Keep all approved and rejected decisions `not_recorded` for ledger status.
- Require an operator identity for all decisions.
- Require a rationale for rejected decisions.
- Fail safely for invalid decisions, duplicate decisions, and unknown inbox
  items.
- Prove operator decision handling does not require common secret environment
  variables or network access.
- Preserve Sprint 7.1 fixture loading, Sprint 7.2 analyzer behavior, Sprint
  7.3 fake proposal behavior, Sprint 7.4 policy behavior, Sprint 7.5 inbox
  behavior, and all existing tests.

## In Scope for Sprint 7.7

- Define structured local ledger/audit records for operator decisions.
- Convert local `OperatorDecisionRecord` objects and matching
  `ApprovalInboxItem` context into `LedgerAuditRecord` objects.
- Keep all ledger records `recorded_locally`.
- Keep all ledger records `not_executed`, `not_called`, and `not_triggered`.
- Preserve upstream decision, proposal, inbox, operator, rationale, snapshot,
  and evidence-reference context.
- Fail safely for mismatched decision/inbox data, duplicate decisions, unknown
  inbox items, and extra evidence-reference keys.
- Prove ledger handling does not require common secret environment variables,
  network access, file persistence, or database persistence.
- Preserve Sprint 7.1 fixture loading, Sprint 7.2 analyzer behavior, Sprint
  7.3 fake proposal behavior, Sprint 7.4 policy behavior, Sprint 7.5 inbox
  behavior, Sprint 7.6 operator decisions, and all existing tests.

## In Scope for Sprint 7.8

- Define structured local dry-run execution result records.
- Convert local `LedgerAuditRecord` objects and matching `ApprovalInboxItem`
  context into `DryRunExecutionResult` objects.
- Keep approved dry-run results `dry_run_completed`.
- Keep rejected dry-run results `dry_run_skipped` with
  `planned_action="no_op_rejected_by_operator"`.
- Keep all dry-run results `not_executed`, `not_called`, and with no external
  side effect.
- Preserve upstream ledger, decision, proposal, inbox, target, and
  evidence-reference context.
- Fail safely for mismatched ledger/inbox data, duplicate ledger records,
  duplicate inbox items, missing inbox references, and malformed local input.
- Prove dry-run handling does not require common secret environment variables,
  network access, file persistence, or database persistence.
- Preserve Sprint 7.1 fixture loading, Sprint 7.2 analyzer behavior, Sprint
  7.3 fake proposal behavior, Sprint 7.4 policy behavior, Sprint 7.5 inbox
  behavior, Sprint 7.6 operator decisions, Sprint 7.7 ledger/audit records, and
  all existing tests.

## In Scope for Sprint 7.9

- Add local raw GitHub-like endpoint fixture payloads.
- Add a local GitHub read adapter contract module.
- Map raw GitHub-like payload dictionaries into the canonical internal snapshot
  dictionary shape.
- Keep raw GitHub-like payloads upstream of the normalizer.
- Exclude issue-like records with `pull_request` markers from canonical issues.
- Convert pull request endpoint records into canonical pull request records.
- Map labels, issue comments, pull reviews, check runs, and status summaries
  deterministically.
- Prove mapped snapshots normalize successfully.
- Prove mapped normalized snapshots can pass through analyzer, fake proposal
  provider, policy guard, approval inbox, operator decision, ledger, and
  dry-run layers.
- Fail safely for malformed or inconsistent local raw-like payloads.
- Prove adapter handling does not require common secret environment variables,
  network access, file persistence, database persistence, GitHub SDKs, or a real
  LLM provider.
- Preserve Sprint 7.1 fixture loading through Sprint 7.8 dry-run behavior and
  all existing tests.

## Out of Scope for Sprint 7.0

- Real GitHub writes.
- Real GitHub issue comments.
- Real label, issue, pull request, branch, commit, or workflow mutation.
- A real LLM provider requirement.
- Runtime GitHub clients.
- Runtime LLM routing.
- Background automation.
- Reading `.env`.
- Reading tokens or credentials.
- Package manager files, dependencies, virtual environments, or generated cache
  files.

## Out of Scope for Sprint 7.1

- Real GitHub reads or writes.
- GitHub API calls or SDKs.
- Reading `.env`.
- Reading tokens or credentials.
- Real LLM providers or provider SDKs.
- Repo analysis or stewardship recommendations.
- Proposal generation.
- Approval inbox runtime.
- Ledger runtime.
- Executor runtime.
- Production readiness claims.

## Out of Scope for Sprint 7.2

- Real GitHub reads or writes.
- GitHub API calls or SDKs.
- Reading `.env`.
- Reading tokens or credentials.
- Real LLM providers or provider SDKs.
- Proposal generation or fake proposal provider behavior.
- Approval inbox runtime.
- Ledger runtime.
- Executor or dry-run executor runtime.
- Background automation.
- Autonomous external side effects.
- Production readiness claims.

## Out of Scope for Sprint 7.3

- Real GitHub reads or writes.
- GitHub API calls or SDKs.
- Reading `.env`.
- Reading tokens or credentials.
- Real LLM providers or provider SDKs.
- Real LLM proposal generation.
- Policy guard runtime.
- Approval inbox runtime.
- Ledger runtime.
- Executor or dry-run executor runtime.
- Background automation.
- Autonomous external side effects.
- Production readiness claims.

## Out of Scope for Sprint 7.4

- Real GitHub reads or writes.
- GitHub API calls, SDKs, or adapter implementation.
- Reading `.env`.
- Reading tokens or credentials.
- Real LLM providers or provider SDKs.
- Real LLM proposal generation.
- Approval decisions.
- Approval inbox runtime.
- Ledger runtime.
- Executor or dry-run executor runtime.
- Background automation.
- Autonomous external side effects.
- Production readiness claims.

## Out of Scope for Sprint 7.5

- Real GitHub reads or writes.
- GitHub API calls, SDKs, or adapter implementation.
- Reading `.env`.
- Reading tokens or credentials.
- Real LLM providers or provider SDKs.
- Real LLM proposal generation.
- Operator approval decision handling.
- Operator rejection handling.
- Ledger runtime.
- Executor or dry-run executor runtime.
- Background automation.
- Autonomous external side effects.
- Production readiness claims.

## Out of Scope for Sprint 7.6

- Real GitHub reads or writes.
- GitHub API calls, SDKs, or adapter implementation.
- Reading `.env`.
- Reading tokens or credentials.
- Real LLM providers or provider SDKs.
- Real LLM proposal generation.
- Ledger runtime.
- Audit persistence runtime.
- Executor or dry-run executor runtime.
- Treating `approved_by_operator` as execution.
- Treating `rejected_by_operator` as a ledgered rejection.
- Background automation.
- Autonomous external side effects.
- Production readiness claims.

## Out of Scope for Sprint 7.7

- Real GitHub reads or writes.
- GitHub API calls, SDKs, or adapter implementation.
- Reading `.env`.
- Reading tokens or credentials.
- Real LLM providers or provider SDKs.
- Real LLM proposal generation.
- Dry-run executor execution.
- Executor runtime.
- Treating a ledger record as execution.
- Treating a ledger record as a GitHub write.
- Treating a ledger record as executor work.
- File persistence.
- Database persistence.
- Durable audit storage.
- Background automation.
- Autonomous external side effects.
- Production readiness claims.

## Out of Scope for Sprint 7.8

- Real GitHub reads or writes.
- GitHub API calls, SDKs, or adapter implementation.
- Reading `.env`.
- Reading tokens or credentials.
- Real LLM providers or provider SDKs.
- Real LLM proposal generation.
- Real executor runtime.
- Executing approved proposals.
- Treating dry-run results as execution.
- Treating dry-run results as GitHub writes.
- Treating dry-run results as external side effects.
- File persistence.
- Database persistence.
- Durable audit storage.
- Background automation.
- Autonomous external side effects.
- Production readiness claims.

## Out of Scope for Sprint 7.9

- Real GitHub reads or writes.
- Live GitHub API calls.
- GitHub authentication.
- GitHub SDKs or provider libraries.
- `requests`, `httpx`, `PyGithub`, `ghapi`, or `octokit`.
- Reading `.env`.
- Reading tokens or credentials.
- Real LLM providers or provider SDKs.
- Real LLM proposal generation.
- Real executor runtime.
- Executing approved proposals.
- Treating raw GitHub-like fixtures as live GitHub data.
- Treating adapter output as proof of complete GitHub API coverage.
- File persistence.
- Database persistence.
- Durable audit storage.
- Background automation.
- Autonomous external side effects.
- Production readiness claims.

## Future Sprint Direction

Future sprints may add, subject to Design Supervisor authorization:

- Sprint 7.12 Artifact 07 closeout and AFDF framework update

The real-mode gates remain after the local GitHub-like fixture adapter
contract. Raw GitHub API responses must pass through a dedicated adapter before
internal analyzer, proposal, policy, approval, ledger, or executor layers
consume them.

## How to Review This Scaffold

Review the following files:

- [Design](docs/design.md)
- [Safety boundaries](docs/safety-boundaries.md)
- [Evidence README](docs/evidence/README.md)
- [Sprint 7.0 validation summary](docs/evidence/artifact-7.0-validation-summary.md)
- [Sprint 7.1 validation summary](docs/evidence/artifact-7.1-validation-summary.md)
- [Sprint 7.2 validation summary](docs/evidence/artifact-7.2-validation-summary.md)
- [Sprint 7.3 validation summary](docs/evidence/artifact-7.3-validation-summary.md)
- [Sprint 7.4 validation summary](docs/evidence/artifact-7.4-validation-summary.md)
- [Sprint 7.5 validation summary](docs/evidence/artifact-7.5-validation-summary.md)
- [Sprint 7.6 validation summary](docs/evidence/artifact-7.6-validation-summary.md)
- [Sprint 7.6R validation summary](docs/evidence/artifact-7.6r-validation-summary.md)
- [Sprint 7.7 validation summary](docs/evidence/artifact-7.7-validation-summary.md)
- [Sprint 7.8 validation summary](docs/evidence/artifact-7.8-validation-summary.md)
- [Sprint 7.9 validation summary](docs/evidence/artifact-7.9-validation-summary.md)
- [Sprint 7.10 validation summary](docs/evidence/artifact-7.10-validation-summary.md)
- [Sprint 7.11 validation summary](docs/evidence/artifact-7.11-validation-summary.md)
- [Tests README](tests/README.md)

Check that every runtime claim is limited to local fixture intake,
normalization, deterministic findings, non-executing fake proposal drafts,
local policy evaluation, pending approval inbox items, local operator decision
records, local ledger/audit records, local dry-run execution results, local
GitHub-like fixture adapter output, local real-read evidence gate records, and
local real-write readiness gate records. No real GitHub path, real LLM
provider, secret read, persistence, executor runtime, or external side effect
has been added.

## Evidence Location

Sprint evidence lives under [docs/evidence](docs/evidence/).

## Known Limitations

- Sprint 7.0 is documentation-only.
- Sprint 7.1 implements only fixture loading and normalization.
- Sprint 7.4 policy evaluations are local routing-safety checks only; they are
  not approval decisions, ledger records, or executor commands.
- Sprint 7.5 approval inbox items are pending local review records only; they
  are not approval decisions, ledger records, executor commands, or persistent
  audit records.
- Sprint 7.6 operator decisions are local decision records only; approvals do
  not execute and rejections do not write ledger/audit records.
- Sprint 7.7 ledger/audit records are local structured audit records only; they
  do not execute, call GitHub, trigger executor work, or persist to files or a
  database.
- Sprint 7.8 dry-run execution results are local simulation records only; they
  do not execute, call GitHub, trigger executor work, or persist to files or a
  database.
- Sprint 7.9 adapter output is local raw-fixture mapping only; it does not call
  GitHub, authenticate, prove live GitHub reads, or prove complete GitHub API
  coverage.
- Sprint 7.10 real-read gate records are local evidence only; they do not prove
  live GitHub reads, authentication, or write readiness.
- Sprint 7.11 write-readiness gate records are local evidence only; they do not
  prove real GitHub writes, write execution, write safety, or production
  readiness.
- Sprint 7.2 implements only deterministic local finding analysis.
- Sprint 7.3 implements only non-executing fake proposal drafts.
- No operational GitHub Repo Steward exists yet.
- No real executor exists in this artifact yet.
- The scaffold does not prove production readiness, real GitHub safety, real LLM
  safety, or end-to-end repository stewardship.
