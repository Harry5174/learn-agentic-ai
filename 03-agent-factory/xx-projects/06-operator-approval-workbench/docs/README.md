# Artifact 06 Documentation

Artifact 06 is the Operator Approval Console / Workbench artifact.

## Read First

- [Artifact 06 spec](specs/artifact-6-operator-approval-workbench.md)
- [Operator workbench architecture](architecture/operator-workbench-architecture.md)
- [Runtime baseline inventory](architecture/runtime-baseline-inventory.md)
- [Development rules](process/development-rules.md)
- [Project status](status/project-status.md)
- [Known limitations](status/known-limitations.md)
- [Roadmap](status/roadmap.md)
- [Interview notes](status/interview-notes.md)
- [Artifact 4 vs Artifact 6](comparisons/artifact-4-vs-artifact-6.md)
- [Artifact 5 vs Artifact 6](comparisons/artifact-5-vs-artifact-6.md)

## Practical Constitution

A6.0 follows the process inherited from Artifact 04 and reinforced by Artifact
05:

- inspect relevant specs, status docs, and process rules before implementation
- state exactly which files were reviewed
- keep one sprint at a time
- keep fake/default behavior before real execution
- require explicit approval before side effects
- avoid live GitHub, credentials, and `.env` access unless separately approved

## Current Runtime Boundary

A6.0 has no `src/app` package. Runtime code remains in Artifact 04.

Artifact 06 will use Artifact 04 as the future runtime baseline and Artifact 05
as release-gate evidence context only.
