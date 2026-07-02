# Artifact 07 - GitHub Repo Steward

Artifact 07 is a GitHub Repo Steward vertical agent scaffold.

## Artifact Status

Artifact 07 is in scaffold status only. It is not a completed runtime artifact.

## Sprint Status

Sprint 7.0 is documentation-first. It establishes the design scaffold, safety
contract, evidence expectations, and implementation boundaries for future
Artifact 07 work.

## Purpose

Artifact 07 prepares a future vertical agent that can inspect repository state,
propose stewardship actions, route those proposals through policy and approval,
and preserve audit evidence. Sprint 7.0 defines that shape without adding a
GitHub client, LLM provider, executor, or external side effect path.

## What This Artifact Demonstrates

Sprint 7.0 demonstrates:

- a repository-owned design scaffold for a future GitHub Repo Steward agent
- explicit fake/local/dry-run defaults
- safety boundaries inherited from Artifacts 04, 05, and 06
- an evidence plan that separates documentation proof from runtime proof
- a placeholder test plan for future implementation sprints

Sprint 7.0 does not demonstrate live repository automation or model-driven
execution.

## Default Mode

The default mode is fake/local/dry-run. The artifact does not perform real
GitHub writes. The artifact does not require a real LLM provider.

Future implementation work should begin from fixture repository snapshots,
deterministic fake proposal providers, local policy checks, approval records,
ledger/audit evidence, and a dry-run executor.

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

## Future Sprint Direction

Future sprints may add:

- fixture repo snapshot loading
- deterministic repo analysis
- fake proposal provider behavior
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
- [Tests placeholder](tests/README.md)

Check that every claim is documentation-scaffold-only and that no runtime source
code, real GitHub path, real LLM provider, secret read, or external side effect
has been added.

## Evidence Location

Sprint 7.0 evidence lives under [docs/evidence](docs/evidence/).

## Known Limitations

- Sprint 7.0 is documentation-only.
- No runtime GitHub Repo Steward exists yet.
- No fixture loader, analyzer, proposal provider, policy guard, approval inbox,
  ledger integration, or executor exists in this artifact yet.
- No tests prove runtime behavior because no runtime behavior is implemented.
- The scaffold does not prove production readiness, real GitHub safety, real LLM
  safety, or end-to-end repository stewardship.
