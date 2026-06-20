# Validation Results

## Completed Commands

### A6.5.1 Demo Flow Fix

Run from the Artifact 06 root:

```bash
uv run pytest tests/test_api_skill_runs.py
uv run pytest tests/test_api_operator_approvals.py
uv run pytest tests/test_operator_workbench_ui.py
uv run pytest
uv run ruff check .
git diff --check
```

Results:

```text
uv run pytest tests/test_api_skill_runs.py
50 passed in 2.92s

uv run pytest tests/test_api_operator_approvals.py
60 passed, 1 warning in 5.89s

uv run pytest tests/test_operator_workbench_ui.py
14 passed in 0.97s

uv run pytest
779 passed, 1 warning in 17.36s

uv run ruff check .
All checks passed!

git diff --check
no output
```

The warning is the existing FastAPI/AnyIO deprecation warning for
`HTTP_422_UNPROCESSABLE_ENTITY` in the rejection-route test path.

### A6.5 Demo Packaging

Run from the Artifact 06 root:

```bash
uv run pytest
uv run ruff check .
git diff --check
```

Results:

```text
uv run pytest
775 passed, 1 warning in 14.95s

uv run ruff check .
All checks passed!

git diff --check
no output
```

Run from the parent workspace root:

```text
git check-ignore -v .env || true
.gitignore:22:*.env	.env

git ls-files .env
no output

git ls-files "*__pycache__*"
no output

git ls-files "*.pyc"
no output

git tag --points-at HEAD
no output
```

Route inventory confirmed the A6 operator routes remain present:

```text
GET /operator/approvals
GET /operator/approvals/{approval_id}
POST /operator/approvals/{approval_id}/approve
GET /operator/approvals/{approval_id}/audit
POST /operator/approvals/{approval_id}/reject
GET /operator/approvals/{approval_id}/status
GET /operator/side-effects/{side_effect_id}
GET /operator/workbench
GET /operator/workbench.css
GET /operator/workbench.js
```

Frontend boundary checks:

```text
find 06-operator-approval-workbench '(' -name "package.json" -o -name "next.config.*" -o -name "node_modules" ')' -print
no output

rg -n "React|Next\\.js|next.config|package.json|node_modules|localStorage|sessionStorage|dangerouslySetInnerHTML" 06-operator-approval-workbench || true
documentation-only negative/deferred references; no package files, storage APIs, or unsafe rendering APIs found
```

## Expected Boundary

The validation confirms:

- no runtime behavior changes
- no `src/app` behavior edits for A6.5
- no package-managed frontend files
- no Next.js configuration
- no `node_modules`
- no live GitHub requirement
- no GitHub token or `.env` requirement
- full Python test suite passes
- Ruff passes
- Markdown diffs have no whitespace errors
