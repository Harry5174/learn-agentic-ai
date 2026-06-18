# A5.3 Validation Results

## Artifact 04 Baseline

```text
git tag --list "artifact-4*":
artifact-4.0-local-demo-real-github-comment-adapter

git rev-parse 9ef8ab8:
9ef8ab86a46bda254137a7c8e5c0984ea9384cf8

git ls-remote --tags origin refs/tags/artifact-4.0-local-demo-real-github-comment-adapter:
9ef8ab86a46bda254137a7c8e5c0984ea9384cf8 refs/tags/artifact-4.0-local-demo-real-github-comment-adapter
```

## Gate 2 Validation

```text
uv run pytest ../05-real-mode-smoke-evidence-release-gate/tests:
21 passed

uv run pytest:
702 passed

uv run ruff check . ../05-real-mode-smoke-evidence-release-gate:
All checks passed!
```

## Preflight Summary

```text
preflight_status: passed
mode: real
real_mode_explicit: true
ci_block_active: false
token_env_name: AGENT_FACTORY_GITHUB_TOKEN
token_present: true
token_value: REDACTED
allowlisted_repo: true
allowlisted_issue: true
fresh_side_effect_mode: new_unique_body
marker_format_verified: true
network_calls_attempted: 0
```

## Post-Live Checks

```text
uv run pytest ../05-real-mode-smoke-evidence-release-gate/tests:
21 passed

uv run pytest:
702 passed

uv run ruff check . ../05-real-mode-smoke-evidence-release-gate:
All checks passed!

git diff --check:
no output

git check-ignore -v .env:
.gitignore:22:*.env .env

git ls-files .env:
no output

git ls-files "*__pycache__*":
no output

git ls-files "*.pyc":
no output

git tag --points-at HEAD:
no output
```

