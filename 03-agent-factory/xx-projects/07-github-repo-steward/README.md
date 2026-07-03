# Artifact 07 - GitHub Repo Steward

Artifact 07 is a GitHub Repo Steward vertical agent scaffold.

## Artifact Status

Artifact 07 has local fixture intake, normalization, deterministic finding
analysis, and non-executing fake proposal drafts. It is not a completed steward
agent.

## Sprint Status

Sprint 7.0 is closed. It established the documentation scaffold, safety
contract, evidence expectations, and implementation boundaries for future
Artifact 07 work.

Sprint 7.1 adds local fixture repository snapshot loading and normalization
only.

Sprint 7.2 adds deterministic repository stewardship findings from the
normalized local fixture snapshot only.

Sprint 7.3 adds a proposal model and deterministic fake proposal provider
boundary that converts findings into non-executing fake proposal drafts only.

## Purpose

Artifact 07 prepares a future vertical agent that can inspect repository state,
propose stewardship actions, route those proposals through policy and approval,
and preserve audit evidence. Sprint 7.3 proves only that a deterministic local
fake GitHub-like snapshot can be loaded, normalized, analyzed into structured
observational findings, and converted into non-executing fake proposal drafts.

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

## Default Mode

The default mode is fake/local/dry-run. The artifact does not perform real
GitHub reads or writes. The artifact does not require a real LLM provider.

Sprint 7.3 begins from fixture repository snapshots, normalizes them, produces
deterministic findings, and converts those findings into non-executing fake
proposal drafts only. Future implementation work may add local policy checks,
approval records, ledger/audit evidence, and a dry-run executor.

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

## Future Sprint Direction

Future sprints may add:

- policy guard rejection tests
- approval inbox integration
- ledger/audit recording
- dry-run executor behavior
- optional real-mode design gates, only after separate approval

## How to Review This Scaffold

Review the following files:

- [Design](docs/design.md)
- [Safety boundaries](docs/safety-boundaries.md)
- [Evidence README](docs/evidence/README.md)
- [Sprint 7.0 validation summary](docs/evidence/artifact-7.0-validation-summary.md)
- [Sprint 7.1 validation summary](docs/evidence/artifact-7.1-validation-summary.md)
- [Sprint 7.2 validation summary](docs/evidence/artifact-7.2-validation-summary.md)
- [Sprint 7.3 validation summary](docs/evidence/artifact-7.3-validation-summary.md)
- [Tests README](tests/README.md)

Check that every runtime claim is limited to local fixture intake and
normalization plus deterministic findings and non-executing fake proposal
drafts. No real GitHub path, real LLM provider, secret read, policy guard
runtime, approval runtime, ledger runtime, executor runtime, or external side
effect has been added.

## Evidence Location

Sprint evidence lives under [docs/evidence](docs/evidence/).

## Known Limitations

- Sprint 7.0 is documentation-only.
- Sprint 7.1 implements only fixture loading and normalization.
- Sprint 7.2 implements only deterministic local finding analysis.
- Sprint 7.3 implements only non-executing fake proposal drafts.
- No operational GitHub Repo Steward exists yet.
- No policy guard, approval inbox, ledger integration, or executor exists in
  this artifact yet.
- The scaffold does not prove production readiness, real GitHub safety, real LLM
  safety, or end-to-end repository stewardship.
