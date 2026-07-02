# Artifact 07 Evidence

## What Evidence Belongs Here

This directory stores evidence for Artifact 07 sprints. For Sprint 7.0, evidence
is limited to documentation-scaffold validation:

- file inventory
- required-document checklist
- hygiene command results
- secret and generated-file checks
- explicit statements about what the scaffold does and does not prove

For Sprint 7.1, evidence is limited to local fixture snapshot loading and
normalization validation:

- file inventory
- local fixture coverage
- pytest results
- compile checks
- hygiene command results
- secret and generated-file checks
- explicit statements about what local fixture normalization does and does not
  prove

Future runtime sprints may add deterministic analyzer outputs, fake proposal
results, approval records, ledger/audit summaries, or dry-run executor
evidence.

## How Sprint 7.0 Evidence Should Be Interpreted

Sprint 7.0 evidence proves only that the documentation scaffold and safety
contract were created and checked. It is local documentation evidence, not live
execution evidence.

## How Sprint 7.1 Evidence Should Be Interpreted

Sprint 7.1 evidence proves only that a committed local fake GitHub-like fixture
snapshot can be loaded and normalized into typed internal records. It is local
offline test evidence, not live GitHub evidence.

## What This Evidence Does Not Prove

Sprint 7.0 and Sprint 7.1 evidence do not prove:

- an operational GitHub Repo Steward runtime exists
- repository analysis works
- proposal generation works
- policy enforcement works at runtime
- approval inbox integration works
- ledger/audit recording works at runtime
- dry-run execution works
- real GitHub reads work
- real GitHub execution works
- real LLM provider integration works
- production readiness

## Why Narrow Evidence Must Not Be Overclaimed

Documentation can define boundaries and planned architecture, but it cannot
prove runtime behavior. Local fixture tests can prove local normalization, but
they cannot prove live GitHub behavior, model-driven proposals, approval
routing, ledger recording, or execution. Any future runtime claim must be backed
by tests, command output, and safety scans from the sprint that implements that
behavior.
