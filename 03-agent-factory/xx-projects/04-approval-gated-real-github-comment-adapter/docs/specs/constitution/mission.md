# Mission

## Artifact Identity

**Name:** Artifact 5 - Approval-Gated Real GitHub Comment Adapter

**Current status:** A5.0 baseline/specification sprint only.

This project was copied from the completed Artifact 4 durable side-effect
ledger. Artifact 4 remains preserved as the local/demo durable fake-client
safety artifact.

Artifact 5 is initialized to define the safety boundary for one future real
external side effect:

```text
post one GitHub issue comment
```

A5.0 does not implement real GitHub execution.

## Mission Statement

Define the safety requirements for moving from a durable fake-client GitHub
comment path to a future approval-gated real GitHub issue-comment adapter.

The project exists to make the trust boundary visible, testable, and explainable
before any real external write is enabled.

## Core Invariant

```text
The LLM proposes.
The harness decides.
```

The proposer is untrusted. The harness owns every security-relevant decision.

## Harness Responsibilities

The harness controls:

- identity
- validation
- policy
- approval
- idempotency
- persistence
- execution
- audit

Request bodies and model output must not define identity, role, scopes, policy
decisions, approval authority, trusted tools, token values, repository
allowlists, real-mode enablement, idempotency markers, or execution authority.

## A5.0 Safety Model

A5.0 defines:

- why Artifact 4 is the baseline
- why local SQLite idempotency is insufficient for real GitHub execution
- GitHub/SQLite crash window
- remote idempotency marker format
- remote reconciliation behavior
- fail-closed behavior for marker lookup failures and ambiguity
- server-side token handling requirements
- minimum-privilege GitHub token guidance
- repository allowlist requirements
- durable audit requirements
- future real-mode testing strategy

## Non-Goals

Artifact 5 A5.0 does not include:

- real GitHub client implementation
- token provider implementation
- environment token loading
- HTTP/network code
- real GitHub API calls
- new runtime side-effect behavior
- remote marker runtime code
- OAuth/OIDC
- MCP
- frontend UI
- deployment
- PR creation
- branch creation
- issue creation
- repo file writes
- workflow dispatch
- multiple real tools
- manual live smoke test
- production-ready claims
- universal exactly-once claims

## Future-Agent Guidance

Future agents should:

- preserve the core invariant
- treat model output like an untrusted external request
- keep authorization, approval, token handling, and execution outside prompts
- keep routes thin and avoid moving policy decisions into HTTP handlers
- keep the repository allowlist server-owned
- keep tokens out of request bodies, model output, tool arguments, logs, audit
  rows, exception messages, and test snapshots
- implement remote marker lookup before any future real post
- fail closed when marker state is ambiguous
- keep automated tests fake/mocked unless a live smoke test is separately
  approved
- describe limitations plainly instead of implying production readiness
