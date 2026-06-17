# A3.4 Adversarial GitHub Side-Effect Safety

## Purpose

A3.4 is a safety-proof sprint for the one A3.3 local/demo GitHub
issue-comment path:

```text
post_github_issue_comment
```

It does not add a new product feature, a second GitHub tool, or real GitHub
network execution. The suite tests whether the current fake-client path keeps
the A3.3 safety boundary intact under adversarial inputs.

## Boundary Under Test

The tested path is:

```text
untrusted SkillProposal
-> ProposalValidator
-> validated scalar arguments
-> repository policy
-> approval gate
-> side_effect_id computation
-> InMemorySideEffectLedger
-> FakeGitHubIssueCommentClient
-> audit evidence
```

Only registry-declared scalar arguments may reach execution:

```text
repository: string
issue_number: integer
comment_body: string
```

The suite verifies that raw proposed arguments, control-plane fields,
credentials, client config, and unsupported payload shapes do not become
executable GitHub comment requests.

## Attack Categories Tested

### Argument Smuggling

Tests cover model-proposed fields such as:

```text
token
github_token
authorization
headers
api_base_url
client_config
transport
real_mode
dry_run
approved
approval_decision
approval_authority
policy_override
risk_override
requires_approval
role
scope
scopes
identity
tool_name
skill_id
skill_version
```

Expected result:

- validation rejects the proposal
- no approval request is created
- policy does not run
- the fake GitHub client is not called
- audit/API evidence exposes safe issue codes, not raw secret values

### Unsupported Payloads

Tests cover object, list, nested, and arbitrary JSON payload attempts for
`repository`, `issue_number`, and `comment_body`.

Expected result:

- invalid payloads are rejected as invalid argument types or unknown arguments
- mixed valid/invalid argument plans do not receive partial acceptance
- execution does not start
- the fake client is not called

### Repository Policy Bypass

Tests cover repository allowlist bypass attempts:

```text
unallowed repository
case variation
trailing space
GitHub URL form
path traversal-like text
model-proposed policy_override
```

Expected result:

- the repository policy denies non-exact allowlist matches
- approval is not requested for denied repositories
- fake-client execution is prevented
- policy denial is audited

### Approval Bypass

Tests cover attempts to bypass the high-risk approval gate:

- valid GitHub comments pause before execution
- unapproved paused runs do not call the fake client
- rejected runs do not call the fake client
- approval by an actor without `approval:approve` fails safely
- public approval routes reject smuggled approval-decision fields
- model-proposed approval fields are rejected as arguments

### Approval-Binding Mutation

A3.3 has a known limitation:

```text
ApprovalDecision does not persist validated_arguments_hash or side_effect_id.
```

A3.4 tests the current architecture around that limitation. The suite proves
that, after a run pauses for approval, mutating the original proposer-side raw
argument dictionary does not change the checkpointed validated action that is
executed. Execution uses the validated arguments captured in graph state, and
the resulting `validated_arguments_hash` and `side_effect_id` are computed from
those validated arguments.

This is not the same as durable persisted approval binding. Stronger approval
binding to persisted `validated_arguments_hash` and `side_effect_id` remains a
future design item.

### Replay And Duplicate Execution

Tests cover:

- duplicate approval after completion is rejected as a non-paused run
- a succeeded ledger hit skips the fake-client call
- repeated direct execution of the same validated action returns a skipped
  ledger-hit result
- changing `comment_body` changes `side_effect_id`
- changing `issue_number` changes `side_effect_id`

This proves local/demo replay suppression for the in-memory ledger only.

### Fake-Client Failure Safety

Tests cover structured fake-client failures:

- failure is recorded in the in-memory ledger
- failure is audited
- failure does not become success
- failure evidence does not leak token-shaped secrets
- the graph does not automatically retry the failed fake-client call

### Network And Token Safety

Tests verify:

- the GitHub comment runtime path has no `requests`, `httpx`, `urllib`,
  `PyGithub`, or `Github(` network implementation
- the runtime GitHub comment path has no automatic `GITHUB_TOKEN`, `GH_TOKEN`,
  `Authorization`, `Bearer`, `os.environ`, or `os.getenv` token-loading path
- the fake client does not read environment tokens
- tests use fake clients and in-process FastAPI clients only

### Audit Completeness

Tests assert audit concepts for:

- validation failure
- repository policy denial
- approval required
- approval granted
- approval rejected
- side-effect id computation
- ledger miss
- ledger hit
- client called
- client not called
- execution skipped
- execution failed

Audit evidence remains safe, structured, and local/demo.

## Result

The A3.4 adversarial suite did not require implementation hardening. The tests
confirmed the A3.3 fake-client path rejects unsafe inputs before execution and
keeps fake-client calls behind validation, policy, approval, and ledger checks.

A3.5 packages this evidence into the Artifact 2 demo and portfolio
documentation. It does not add new runtime behavior.

## What Remains Local/Demo

A3.4 does not change the current product boundary. The project still uses:

- process-local graph checkpoints
- in-memory audit events
- in-memory side-effect ledger
- static demo API-key identities
- fake-client GitHub comment simulation
- no persistent replay guarantees
- no real GitHub network execution
- no automatic GitHub token loading

## What This Is Not

A3.4 is not production security infrastructure. It does not add:

- real GitHub client code
- durable replay or idempotency guarantees
- durable audit storage
- arbitrary repository targeting
- OAuth/OIDC
- JWT validation
- MCP
- workflow dispatch
- PR creation
- branch creation
- issue creation
- repo file writes
- frontend
- production deployment
- autonomous real execution
