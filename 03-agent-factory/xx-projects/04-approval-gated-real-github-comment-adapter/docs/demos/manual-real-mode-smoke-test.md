# Manual Real-Mode Smoke Test

This page documents an optional manual smoke test for the one
approval-gated real GitHub issue-comment path.

Manual smoke execution is disabled by default and was not run as part of A5.5
validation. Do not run it unless the Product Owner explicitly approves live
execution in the implementation session.

## Status

```text
documented but not run
not run in A5.5
```

## Important Safety Statements

- This test is **disabled by default**.
- This test is **optional**.
- This test **requires explicit Product Owner approval** before any live
  execution.
- This test uses **only the allowlisted test repository**.
- This test uses **`.env` locally** for token storage.
- The token **must never be pasted into ChatGPT** or any LLM interface.
- The token **must never be committed** to version control.
- This test **posts at most one comment for an approved `side_effect_id`**.
- **Remote marker lookup happens before posting.**
- This test was **not run in A5.5**.

## Scope

The only allowed live side effect is:

```text
post one GitHub issue comment
```

The prepared manual target is:

```text
Harry5174/artifact-5-github-comment-test#1
```

Do not use arbitrary repositories. Do not widen the allowlist. Do not use this
guide for issue creation, PR creation, branch creation, repo file writes,
workflow dispatch, labels, milestones, assignees, edit, or delete operations.

## Preconditions

Before any live run:

- obtain explicit Product Owner approval for the manual smoke execution
- verify `.env` is ignored, untracked, and unstaged without printing it
- keep `AGENT_FACTORY_GITHUB_TOKEN` server-side only
- use a fine-grained token limited to the prepared repository
- require Issues read/write permission only
- keep real mode disabled unless trusted server-side config enables it
- keep automated tests mocked and credential-free

Safe `.env` tracking checks:

```bash
git status --short -- .env
git ls-files .env
git check-ignore -v .env
```

Do not run `cat .env`, do not source `.env` in automated tests, and do not print
the token.

## Required Real-Mode Configuration

A live smoke must use trusted server-side dependency injection equivalent to:

```python
GitHubRealModeConfig(
    enabled=True,
    allowed_repositories=("Harry5174/artifact-5-github-comment-test",),
    client_mode="real",
)
```

The token provider must read `AGENT_FACTORY_GITHUB_TOKEN` from server-side
environment only. Request bodies, model output, tool arguments, and approval
payloads must not provide the token, enable real mode, or widen the repository
allowlist.

## Expected Safety Order

The live path must complete local gates before any network call:

```text
1. validate scalar arguments
2. enforce exact repository allowlist
3. compute validated_arguments_hash
4. compute side_effect_id
5. check local durable side-effect ledger
6. suppress if local side effect already succeeded
7. verify durable approval binding for exact side_effect_id + hash
8. verify explicit real-mode config
9. load server-side token
10. list remote issue comments
11. check remote idempotency marker
12. reconcile if marker exists, without posting
13. fail closed for mismatch, ambiguity, lookup failure, or incomplete listing
14. append marker and create one issue comment only when marker is absent
15. persist external comment id/url
16. record durable audit
```

Posted comment bodies must include:

```html
<!-- agent_factory:v1 side_effect_id=<side_effect_id> args_hash=<validated_arguments_hash> -->
```

The marker is idempotency evidence only. It is not authorization and does not
bypass durable approval binding.

## Expected Evidence

A successful smoke report may include:

- repository and issue number
- side effect id
- validated arguments hash
- external comment id/url
- audit event names
- confirmation that remote marker lookup occurred before posting
- confirmation that `.env` remained untracked and unstaged

The report must not include:

- token values
- Authorization header values
- raw response headers
- raw unredacted transport exceptions
- `.env` contents
