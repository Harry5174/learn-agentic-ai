# GitHub Comment Tool Demo

This guide packages the Artifact 3 GitHub issue-comment path for local demos
and portfolio review.

The path is local/demo only:

```text
post_github_issue_comment
```

It uses `FakeGitHubIssueCommentClient`. It does not call the GitHub API, does
not require a GitHub token, and does not make a network call.

## What Is Runnable Through Public HTTP

The public HTTP API can run these commands directly:

- start the local API
- list registered skills, including `post_github_issue_comment`
- create the default fake-proposer low-risk skill run
- read a run
- read a run audit trail
- reject disabled HTTP `llm` mode

The default running HTTP API does not expose a request field that selects the
GitHub-comment fake proposer scenario. The request schema accepts
`requested_skill_id`, but the route currently delegates to the configured
server-side proposer instead of forcing a skill from curl.

For that reason, GitHub-comment approval, rejection, policy-denial, replay, and
failure examples below are labeled as representative/test-backed evidence.
They are backed by tests that inject a GitHub-comment proposer into
`SkillGraphService`.

## 1. Start The API

From this project folder:

```bash
uv run app
```

The app listens on:

```text
http://127.0.0.1:8000
```

Equivalent direct uvicorn command:

```bash
uv run uvicorn app.api.main:app --reload
```

Demo API keys:

```bash
VIEWER_KEY=viewer-dev-key
OPERATOR_KEY=operator-dev-key
ADMIN_KEY=admin-dev-key
BASE_URL=http://127.0.0.1:8000
```

These are static local/demo credentials, not production identity.

## 2. List Skills

Runnable public HTTP command:

```bash
curl -s "$BASE_URL/skills"
```

The response includes safe public metadata for the GitHub comment skill:

```json
{
  "skill_id": "post_github_issue_comment",
  "version": "1.0",
  "name": "Post GitHub issue comment",
  "required_scopes": ["tools:post_github_comment"],
  "risk_level": "high",
  "steps": [
    {
      "step_id": "post_comment",
      "tool_name": "post_github_issue_comment",
      "risk_level": "high",
      "required_scopes": ["tools:post_github_comment"]
    }
  ]
}
```

This listing does not execute anything. It does not expose callables,
checkpoints, graph internals, or fake-client objects.

## 3. Create A GitHub Comment Skill Run

Representative/test-backed evidence:

The GitHub-comment path is exercised by tests using a configured
`FakeProposer(FakeProposalScenario.VALID_GITHUB_COMMENT)`. The default public
HTTP API cannot select that scenario from curl.

The test-backed request shape is the normal skill-run creation endpoint:

```bash
curl -s -X POST "$BASE_URL/skill-runs" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ADMIN_KEY" \
  -d '{"task": "Post a local/demo fake GitHub issue comment."}'
```

Representative paused response fields:

```json
{
  "status": "paused_for_approval",
  "selected_skill_id": "post_github_issue_comment",
  "validation_status": "accepted",
  "approval_required": true,
  "approval_status": "pending",
  "risk_level": "high",
  "execution": {
    "attempted_step_count": 0,
    "completed_step_count": 0,
    "tool_names": [],
    "dry_run": true
  }
}
```

Evidence:

- `tests/test_github_comment_skill.py::test_github_comment_skill_uses_existing_http_lifecycle`
- `tests/test_github_comment_skill.py::test_github_comment_pauses_for_approval_without_client_call`

Fake client only. No token required. No network call.

## 4. Observe Approval-Required State

Representative/test-backed evidence:

A valid GitHub comment proposal is high risk. The graph pauses before
fake-client execution.

Expected state:

- `status: "paused_for_approval"`
- `approval_required: true`
- `approval_status: "pending"`
- zero attempted execution steps
- fake client has not been called

The approval request contains validated scalar arguments only:

```json
{
  "repository": "Harry5174/learn-agentic-ai",
  "issue_number": 1,
  "comment_body": "A deterministic fake GitHub comment."
}
```

Evidence:

- `tests/test_github_comment_skill.py::test_github_comment_pauses_for_approval_without_client_call`
- `tests/test_adversarial_github_side_effect_safety.py::test_high_risk_github_comment_pauses_before_any_fake_client_call`

## 5. Inspect Run State

Runnable public HTTP command when a run exists:

```bash
curl -s "$BASE_URL/skill-runs/RUN_ID"
```

Representative GitHub-comment run fields:

```json
{
  "selected_skill_id": "post_github_issue_comment",
  "validation_status": "accepted",
  "approval_required": true,
  "approval_status": "pending",
  "execution": {
    "attempted_step_count": 0,
    "completed_step_count": 0,
    "tool_names": [],
    "dry_run": true
  }
}
```

The public response does not expose graph objects, checkpointer internals,
server-derived identity objects, approval actors, or internal step-argument
stores.

## 6. Reject Path Demo

Representative/test-backed evidence:

When a GitHub comment run is paused, rejection finalizes the run without a fake
GitHub client call.

Runnable approval route shape when a paused run exists:

```bash
curl -s -X POST "$BASE_URL/skill-runs/RUN_ID/reject" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ADMIN_KEY" \
  -d '{"reason": "Do not post even a fake comment."}'
```

Representative rejected response fields:

```json
{
  "status": "rejected",
  "approval_status": "rejected",
  "execution": {
    "attempted_step_count": 0,
    "completed_step_count": 0,
    "tool_names": [],
    "dry_run": true
  }
}
```

Evidence:

- `tests/test_github_comment_skill.py::test_rejected_github_comment_run_does_not_call_fake_client`
- `tests/test_adversarial_github_side_effect_safety.py::test_rejected_github_comment_approval_never_calls_fake_client`

Fake client only. No token required. No network call.

## 7. Approve Path Demo

Representative/test-backed evidence:

When an authorized admin approves a paused GitHub comment run, the graph resumes
and calls `FakeGitHubIssueCommentClient` after validation, repository policy,
approval, side-effect id computation, and in-memory ledger check.

Runnable approval route shape when a paused run exists:

```bash
curl -s -X POST "$BASE_URL/skill-runs/RUN_ID/approve" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ADMIN_KEY" \
  -d '{"reason": "Approved local/demo fake GitHub comment."}'
```

Representative approved response fields:

```json
{
  "status": "completed",
  "approval_status": "approved",
  "execution": {
    "attempted_step_count": 1,
    "completed_step_count": 1,
    "tool_names": ["post_github_issue_comment"],
    "dry_run": true
  }
}
```

Internal test-backed result evidence includes:

- `client_called: true`
- `ledger_miss: true`
- `side_effect_status: "succeeded"`
- `mode: "fake_client"`

Evidence:

- `tests/test_github_comment_skill.py::test_approved_github_comment_calls_fake_client_after_gates_and_records_ledger`
- `tests/test_github_comment_skill.py::test_github_comment_skill_uses_existing_http_lifecycle`

Fake client only. No token required. No network call.

## 8. Inspect Audit Evidence

Runnable public HTTP command when a run exists:

```bash
curl -s "$BASE_URL/skill-runs/RUN_ID/audit"
```

Representative/test-backed GitHub-comment audit evidence includes:

- `proposal_validation` metadata
- repository policy decision
- `github_comment_approval_required`
- `github_comment_approval_granted` or `github_comment_approval_rejected`
- `github_comment_side_effect_id_computed`
- `github_comment_ledger_miss` or `github_comment_ledger_hit`
- `github_comment_client_called` or `github_comment_client_not_called`
- `github_comment_executed`, `github_comment_skipped`, or `github_comment_failed`
- `real_github_network_call: false` on GitHub comment execution metadata

Evidence:

- `tests/test_adversarial_github_side_effect_safety.py::test_audit_concepts_cover_github_comment_safety_lifecycle`
- `src/app/skill_graph/graph.py` GitHub comment audit metadata helpers

Audit is in memory and process-local.

## 9. Duplicate / Replay Skip

Representative/test-backed evidence:

The local/demo side-effect id is derived from:

```text
skill_run_id
step_id
tool_name
validated_arguments_hash
```

If the in-memory ledger already has a succeeded record for the same
side-effect id, the fake-client call is skipped and a cached/skipped result is
returned.

Representative result fields:

```json
{
  "ledger_hit": true,
  "client_called": false,
  "skipped": true,
  "skip_reason": "side_effect_already_succeeded"
}
```

Evidence:

- `tests/test_github_comment_skill.py::test_github_comment_replay_skips_duplicate_fake_client_call_after_success`
- `tests/test_adversarial_github_side_effect_safety.py::test_ledger_success_hit_skips_fake_client_and_is_audited`

This is in-memory local/demo replay suppression only. It is not a persistent
replay guarantee.

## 10. Policy-Denied Repository Example

Representative/test-backed evidence:

The default local/demo allowlist contains:

```text
Harry5174/learn-agentic-ai
```

An unallowed repository is denied before approval or fake-client execution.

Representative denied fields:

```json
{
  "status": "denied",
  "approval_required": true,
  "approval_status": "pending",
  "execution": {
    "attempted_step_count": 0,
    "completed_step_count": 0,
    "tool_names": [],
    "dry_run": true
  }
}
```

Internal test-backed evidence:

- policy decision is `deny`
- `github_comment_policy_denied` is audited
- fake client has zero calls

Evidence:

- `tests/test_github_comment_skill.py::test_unallowed_repository_is_denied_before_approval_or_client_call`
- `tests/test_adversarial_github_side_effect_safety.py::test_github_comment_repository_policy_bypass_attempts_are_denied`

No arbitrary repository targeting is implemented.

## 11. Fake-Client-Only Behavior

Artifact 3 currently uses:

- `GitHubIssueCommentClient` protocol
- `FakeGitHubIssueCommentClient`
- `InMemorySideEffectLedger`
- local/demo repository allowlist

It does not include:

- real GitHub API adapter
- GitHub token loading
- workflow dispatch
- PR creation
- issue creation
- branch creation
- repo file writes
- durable audit storage
- durable ledger storage

Every GitHub-comment path in this artifact is fake-client/local-demo only. No
token required. No network call.

## 12. Known Limitations

Current limits:

- public HTTP cannot select the GitHub-comment fake proposer scenario from curl
- skill-run state is process-local
- checkpoints are in memory
- audit events are in memory
- side-effect ledger is in memory
- `ApprovalDecision` does not persist `validated_arguments_hash`
- `ApprovalDecision` does not persist `side_effect_id`
- object/list/nested arguments are unsupported
- mixed valid/invalid argument plans are rejected rather than partially
  accepted
- live HTTP LLM mode is disabled
- no real GitHub execution is implemented

For the broader list, see [../status/known-limitations.md](../status/known-limitations.md).
