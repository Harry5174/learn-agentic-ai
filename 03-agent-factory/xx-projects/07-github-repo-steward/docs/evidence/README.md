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

For Sprint 7.2, evidence is limited to deterministic analyzer validation:

- file inventory
- analyzer rule coverage
- deterministic finding ID and order checks
- no-mutation checks
- no-secret and no-network checks
- pytest results
- compile checks
- hygiene command results
- explicit statements about what local deterministic findings do and do not
  prove

For Sprint 7.3, evidence is limited to fake proposal draft validation:

- file inventory
- proposal model coverage
- fake provider mapping coverage
- deterministic proposal ID and order checks
- no-mutation checks
- no-secret and no-network checks
- pytest results
- compile checks
- hygiene command results
- explicit statements about what fake proposal drafts do and do not prove

For Sprint 7.4, evidence is limited to local proposal policy evaluation:

- file inventory
- policy evaluation model coverage
- deterministic evaluation ID and order checks
- safe-for-operator-review allow checks
- blocked-by-policy reason checks
- no-mutation checks
- no-secret and no-network checks
- pytest results
- compile checks
- hygiene command results
- explicit classification of intentional local guard-pattern literals
- explicit statements about what local policy evaluation does and does not
  prove

Future runtime sprints may add approval records, ledger/audit summaries, or
dry-run executor evidence.

## How Sprint 7.0 Evidence Should Be Interpreted

Sprint 7.0 evidence proves only that the documentation scaffold and safety
contract were created and checked. It is local documentation evidence, not live
execution evidence.

## How Sprint 7.1 Evidence Should Be Interpreted

Sprint 7.1 evidence proves only that a committed local fake GitHub-like fixture
snapshot can be loaded and normalized into typed internal records. It is local
offline test evidence, not live GitHub evidence.

## How Sprint 7.2 Evidence Should Be Interpreted

Sprint 7.2 evidence proves only that normalized local fixture data can be
converted into deterministic structured findings. It is local offline test
evidence, not live GitHub evidence and not proposal-provider evidence.

## How Sprint 7.3 Evidence Should Be Interpreted

Sprint 7.3 evidence proves only that analyzer findings can be converted into
deterministic non-executing fake proposal drafts. It is local offline test
evidence, not live GitHub evidence, not real LLM evidence, and not evidence of
approval or execution capability.

## How Sprint 7.4 Evidence Should Be Interpreted

Sprint 7.4 evidence proves only that non-executing fake proposal drafts can be
evaluated by deterministic local policy rules. The
`allowed_for_operator_review` verdict is a routing-safety result for a future
operator-review layer, not approval. It is local offline test evidence, not
live GitHub evidence, not real LLM evidence, and not evidence of approval,
ledger, inbox, dry-run executor, or execution capability.

## What This Evidence Does Not Prove

Sprint 7.0, Sprint 7.1, Sprint 7.2, Sprint 7.3, and Sprint 7.4 evidence do not
prove:

- an operational GitHub Repo Steward runtime exists
- real LLM proposal generation works
- approval-gated runtime works
- approval inbox integration works
- ledger/audit recording works at runtime
- dry-run execution works
- real GitHub reads work
- GitHub API adapter correctness
- real GitHub execution works
- real LLM provider integration works
- production readiness

## Why Narrow Evidence Must Not Be Overclaimed

Documentation can define boundaries and planned architecture, but it cannot
prove runtime behavior. Local fixture tests can prove local normalization, but
they cannot prove live GitHub behavior. Local analyzer tests can prove
deterministic findings, but they cannot prove model-driven proposals, approval
routing, ledger recording, or execution. Local fake provider tests can prove
non-executing fake proposal drafts, but they cannot prove policy decisions,
approval decisions, ledger recording, executor behavior, real GitHub behavior,
or real LLM behavior. Local policy guard tests can prove deterministic policy
evaluation, but they cannot prove approval decisions, approval inbox behavior,
ledger recording, executor behavior, real GitHub behavior, or real LLM
behavior. Any future runtime claim must be backed by tests, command output, and
safety scans from the sprint that implements that behavior.
