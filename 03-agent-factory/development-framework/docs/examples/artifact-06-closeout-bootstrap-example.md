# Artifact 06 Closeout Bootstrap Example

> This is an example of a next-session bootstrap for verifying Artifact 06 final closeout, publish, and tag state.

---

## Session Purpose

Verify whether Artifact 06 (Operator Approval Console / Workbench) has completed its final closeout:

- All sprints green-gated
- Branch merged to main
- Tag applied (if applicable)
- Documentation accurate

This is a verification session, not an implementation session.

---

## What This Session Knows

- Artifact 06 reached sprint A6.5 (demo packaging and portfolio story)
- Sprints A6.5.1 (demo flow fix) and A6.5.2 (warning cleanup) were also completed
- All three branches exist on origin
- The `xx-projects/README.md` lists Artifact 06 status as "Current local/demo workbench artifact (A6.5)"

---

## What This Session Must Not Assume

- Do not assume Artifact 06 branches have been merged to main
- Do not assume a release tag exists
- Do not assume the parent `03-agent-factory/README.md` has been updated to reflect Artifact 06
- Do not assume all sprints are green-gated unless evidence shows it

---

## Required First Commands

Run these commands to verify the current state:

```bash
git branch --show-current
git status -sb
git rev-parse HEAD
git log --oneline -8
```

Check for tag state:

```bash
git tag --points-at HEAD
git tag -l "artifact-6*"
```

Check for tracked sensitive files:

```bash
git check-ignore -v .env || true
git ls-files .env
```

Check branch merge status:

```bash
git branch -a --merged main | grep artifact-6 || echo "No artifact-6 branches merged to main"
```

---

## Verification Checklist

- [ ] Confirm current branch is `main`
- [ ] Confirm working tree is clean
- [ ] Check if A6.5, A6.5.1, and A6.5.2 branches are merged to main
- [ ] Check if a release tag exists for Artifact 06
- [ ] Verify `xx-projects/README.md` Artifact 06 status is accurate
- [ ] Verify `03-agent-factory/README.md` reflects Artifact 06 (or note that it does not)
- [ ] Confirm `.env` is not tracked
- [ ] Run token scan against Artifact 06 folder

```bash
rg -n "ghp_|github_pat_|gho_|ghu_|ghs_|ghr_|Bearer " \
  03-agent-factory/xx-projects/06-operator-approval-workbench || true
```

---

## Expected Output

- [ ] Closeout verification report stating:
  - Branch merge status
  - Tag status
  - Documentation accuracy
  - Safety verification results
- [ ] If not fully closed out: specific list of remaining actions
- [ ] If fully closed out: confirmation that Phase 02 can be considered complete

---

## Safety Rules

- Do not run the operator workbench application
- Do not execute live GitHub operations
- Do not read `.env`
- Do not require credentials
- This is a verification-only session
