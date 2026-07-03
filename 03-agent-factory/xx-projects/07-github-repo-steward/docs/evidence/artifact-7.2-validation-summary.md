# Artifact 7.2 Validation Summary

## Scope

Sprint 7.2 validates deterministic local repository stewardship findings for
Artifact 07. It does not validate proposal generation, approval routing, ledger
recording, execution, real GitHub access, or real LLM integration.

## What Was Added

- Analyzer module: `src/github_repo_steward/analyzer.py`
- Finding model: `RepoFinding`
- Public analyzer export: `analyze_repo_snapshot`
- Analyzer tests for findings, determinism, no mutation, no secret environment
  requirement, and no network sockets

## Analyzer Rules Implemented

- `issue_missing_reproduction`
- `issue_stale_no_maintainer_response`
- `pull_request_failing_ci`
- `pull_request_waiting_for_review`

## Checklist

| Check | Status | Evidence |
|-------|--------|----------|
| Default fake fixture loads | Verified | `tests/test_repo_snapshot.py` |
| Default fake fixture normalizes | Verified | `tests/test_normalizer.py` |
| Analyzer returns structured findings | Verified | `tests/test_analyzer.py` |
| Finding IDs are deterministic | Verified | `tests/test_analyzer.py` |
| Finding order is deterministic | Verified | `tests/test_analyzer_determinism.py` |
| Analyzer does not mutate the snapshot | Verified | `tests/test_analyzer_determinism.py` |
| Analyzer handles empty snapshots | Verified | `tests/test_analyzer.py` |
| Analyzer works without common secret env vars | Verified | `tests/test_analyzer_no_side_effects.py` |
| Analyzer does not open network sockets | Verified | `tests/test_analyzer_no_side_effects.py` |
| No real GitHub code added | Verified | Source inspection and safety scans |
| No real LLM requirement added | Verified | Source inspection and safety scans |
| No `.env` read or created | Verified | Git hygiene checks |
| No generated cache files tracked | Verified | Git hygiene checks |

## Validation Commands

- Artifact test suite with bytecode and pytest cache disabled.
- Compile check with isolated Python cache prefix.
- Git diff whitespace check.
- Artifact file inventory.
- Secret-pattern scan.
- Local-path scan.
- `.env`, `__pycache__`, and `.pyc` tracked-file checks.

## Interpretation

This summary supports only the Sprint 7.2 local deterministic analyzer findings
claim after the listed tests and checks pass.

## What This Summary Does Not Prove

This summary does not prove LLM proposal generation, fake proposal provider
behavior, policy guard runtime, approval-gated runtime, ledger/audit runtime,
dry-run execution, real GitHub integration, or production readiness.

## Known Limitations

- Findings are rule-based observations, not executable proposals.
- Stale issue maintainer-response detection uses `comments_count == 0` as the
  Sprint 7.2 local fixture proxy.
- The analyzer uses only normalized local fixture fields and does not inspect a
  live repository.

## Next Recommended Sprint

Artifact 7.3 - Proposal Model and Fake Proposal Provider Boundary, subject to
Design Supervisor approval.
