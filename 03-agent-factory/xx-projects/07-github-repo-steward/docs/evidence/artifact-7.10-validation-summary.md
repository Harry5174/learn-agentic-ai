# Artifact 7.10 Validation Summary

## Sprint Objective

Sprint 7.10 validates a deterministic local real-read mode evidence gate for
Artifact 07. The gate records whether fake/default mode is allowed, whether a
real-read request is blocked, or whether a real-read request has only enough
metadata for read-only preflight consideration.

No live-read authorization was present for this sprint. No live GitHub read was
attempted. Sprint 7.10 proves the evidence gate and fake/default adapter path
only.

## Files Added

- `src/github_repo_steward/real_read_gate.py`
- `tests/test_real_read_gate.py`
- `tests/test_real_read_gate_determinism.py`
- `tests/test_real_read_gate_no_side_effects.py`
- `docs/evidence/artifact-7.10-validation-summary.md`

## Files Modified

- `src/github_repo_steward/models.py`
- `src/github_repo_steward/__init__.py`
- `README.md`
- `docs/design.md`
- `docs/safety-boundaries.md`
- `docs/evidence/README.md`
- `tests/README.md`
- Parent artifact index: `../README.md`

## Real-Read Gate Model Added

- `RealReadGateError`
- `RealReadRequest`
- `RealReadGateEvaluation`
- `RealReadEvidenceRecord`

Gate evaluations preserve:

- deterministic evaluation identity
- request mode
- repository full name
- verdict
- reasons
- adapter boundary requirement
- GitHub status
- network status
- write status
- secret status
- whether it is safe to attempt a future read-only preflight

Evidence records preserve:

- deterministic evidence identity
- evaluation identity
- repository full name
- mode
- adapter boundary status
- raw payload status
- canonical snapshot status
- normalization status
- pipeline status
- GitHub status
- write status
- secret status
- summary

## Real-Read Gate Behavior Added

- Allows fake/default mode without credentials.
- Blocks real-read requests without Product Owner authorization.
- Blocks real-read requests without repository target.
- Blocks real-read requests without safe credential-handling metadata.
- Blocks real-read requests if the Sprint 7.9 adapter boundary is disabled.
- Blocks real-read requests if write operations are allowed.
- Allows a read-only preflight metadata state only when explicit Product Owner
  authorization, repository target, safe credential metadata, adapter boundary,
  write prohibition, and network preflight intent are present.
- Keeps preflight allowed distinct from live-read evidence.
- Produces deterministic evaluation IDs.
- Produces deterministic evidence IDs.
- Represents fake/default adapter-path evidence.
- Represents blocked real-read evidence.
- Does not mutate request or evaluation objects.
- Does not call GitHub.
- Does not use network.
- Does not read `.env`.
- Does not require secrets.
- Does not add GitHub SDKs.
- Does not add real LLM provider dependencies.
- Does not execute proposals.
- Does not add file or database persistence.

## Validation Commands Run

- `git status -sb`
- `git diff --check`
- Artifact 07 file inventory command from the sprint prompt.
- Token, credential-name, and live-host-pattern scan from the sprint prompt.
- Local-path scan from the sprint prompt.
- `git ls-files .env`
- Tracked Python cache checks from the sprint prompt.
- Artifact 07 pytest suite with bytecode and pytest cache disabled.
- Compile check with an isolated Python cache prefix outside the artifact tree.

## Test Results

- Artifact 07 pytest suite: 177 passed.
- Compile check: passed.
- Existing Sprint 7.1 through Sprint 7.9 tests remain preserved.

## Safety Scan Results

- `git diff --check` passed.
- `.env` remains untracked.
- No tracked `__pycache__` files.
- No tracked `.pyc` files.
- Local-path scan produced no matches.
- No live GitHub read was attempted.
- No real GitHub write path was added.
- No GitHub SDK or provider dependency was added.
- No real LLM provider dependency was added.
- No real executor runtime was added.
- No file or database persistence was added.

Token and credential-name scan hits are intentional local guard-pattern, test,
and documentation strings. They are not secret values.

## Live-Read Authorization Status

Live-read authorization was not present in the IDE session.

## Live-Read Attempt Status

No live GitHub read was attempted. No GitHub API was called by Sprint 7.10 gate
code or tests.

## What Sprint 7.10 Proves

- Real-read mode has an explicit evidence gate.
- Real-read mode is blocked by default.
- Fake/default mode remains the default.
- Fake/default mode is allowed without credentials.
- Real-read requests without Product Owner authorization are denied.
- Real-read requests without a repository target are denied.
- Real-read requests without safe credential-handling metadata are denied.
- Real-read requests that would bypass the Sprint 7.9 adapter boundary are
  denied.
- Real-read requests that imply write behavior are denied.
- Read evidence records are structured.
- Read evidence records are deterministic.
- Local raw GitHub-like fixture payloads still map through the adapter boundary.
- Mapped snapshots still normalize successfully.
- Mapped normalized snapshots still pass through analyzer, fake proposal
  provider, policy guard, approval inbox, operator decision, ledger, and dry-run
  layers.
- Gate tests require no network by default.
- Gate tests require no secrets by default.
- Gate tests require no real GitHub provider by default.
- Prior Sprint 7.1 through Sprint 7.9 behavior remains covered by tests.

## What Sprint 7.10 Does Not Prove

- live GitHub read behavior
- live GitHub read safety
- live GitHub authentication behavior
- real GitHub writes
- GitHub write readiness
- GitHub write safety
- GitHub App integration
- GitHub OAuth integration
- real GitHub payload coverage completeness
- real executor runtime
- real LLM integration
- production readiness

## Known Limitations

- Gate records are in-memory dataclass records only.
- The gate evaluates local request metadata only.
- The gate does not authenticate.
- The gate does not call live APIs.
- The gate does not capture live raw payloads.
- The gate does not normalize live GitHub responses.
- The gate does not introduce real execution or persistence.
- Read-only preflight allowed is not proof that a live read happened.

## Next Recommended Sprint

Artifact 7.11 - Real-Write Readiness Gate, subject to Design Supervisor
approval.
