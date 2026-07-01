# Pre-Design Repository Inspection

Run these safe commands to inspect the repository state before beginning Artifact 07 design:

```bash
cd "$(git rev-parse --show-toplevel)"
git branch --show-current
git status -sb
git status --short
git log --oneline -14
git rev-parse HEAD
git tag --points-at HEAD
git ls-remote --heads origin main
find 03-agent-factory/development-framework -maxdepth 6 -type f | sort | sed -n '1,360p'
wc -l 03-agent-factory/development-framework/docs/templates/*-template.md
find 03-agent-factory/xx-projects -maxdepth 2 -type d | sort
```

Also run these hygiene and safety checks:

```bash
git diff --check
git check-ignore -v .env || true
git ls-files .env
git ls-files "*__pycache__*"
git ls-files "*.pyc"
```
*(Do not include commands that print secrets).*
