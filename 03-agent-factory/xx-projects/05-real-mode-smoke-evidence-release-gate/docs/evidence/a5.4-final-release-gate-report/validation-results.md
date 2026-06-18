# Validation Results

## Branch And Baseline

```text
branch: artifact-5.4-replay-negative-release-gate-report
starting HEAD: 1bc2a0b159ee2ece6041787420dba8d188c33f3f
starting status: clean
```

## Commands Run

From Artifact 04 project root:

```text
uv run pytest ../05-real-mode-smoke-evidence-release-gate/tests
uv run pytest
uv run ruff check . ../05-real-mode-smoke-evidence-release-gate
```

From repository root:

```text
git diff --check
git status -sb
git status --short
git check-ignore -v .env || true
git ls-files .env
git ls-files "*__pycache__*"
git ls-files "*.pyc"
git tag --points-at HEAD
```

Redaction scans:

```text
required token-like pattern scan against Artifact 05 docs/evidence
required intentional safety-wording scan against Artifact 05 docs/evidence
```

## Results

```text
uv run pytest ../05-real-mode-smoke-evidence-release-gate/tests: 21 passed
uv run pytest: 702 passed
uv run ruff check . ../05-real-mode-smoke-evidence-release-gate: All checks passed!
git diff --check: no output
git status -sb: expected A5.4 docs/evidence modifications before commit
git status --short: expected A5.4 docs/evidence modifications before commit
git check-ignore -v .env || true: .gitignore:22:*.env .env
git ls-files .env: no output
git ls-files "*__pycache__*": no output
git ls-files "*.pyc": no output
git tag --points-at HEAD: no output
token-like redaction scan: no output after removing self-triggering command text
intentional safety-wording scan: safe intentional wording only
```

No actual token-like value appeared in the evidence bundle. The intentional
safety-wording scan matched redacted evidence language only.
