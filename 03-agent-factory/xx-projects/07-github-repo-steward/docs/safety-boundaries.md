# Artifact 07 Safety Boundaries

## 1. Safety Invariants

- Use fake/local/dry-run behavior by default.
- Do not read `.env`.
- Do not read, print, or require credentials in Sprint 7.0 or Sprint 7.1.
- Do not call GitHub APIs in Sprint 7.1.
- Do not perform real GitHub reads or writes in Sprint 7.1.
- Do not run live external side effects.
- Treat proposal-provider output as untrusted.
- Validate and policy-check proposed actions before approval.
- Require operator approval before any future external side effect.
- Record ledger/audit evidence before claiming execution success.
- Preserve the invariant: LLM proposes; harness decides; operator approves;
  executor acts only after approval.

## 2. Default-Deny Behavior

If a future proposal is ambiguous, unsafe, unsupported, outside policy, missing
evidence, or not explicitly approved, the harness should reject it or keep it in
dry-run/non-executing state. Default-deny is the expected behavior for all
unclear cases.

## 3. Fake GitHub Boundary

Sprint 7.1 adds a local fixture snapshot and normalizer only. It does not add a
GitHub client, GitHub SDK, GitHub API call, or real repository read path. Future
fake GitHub behavior should use local fixtures or fake adapters only. Fake
behavior may support deterministic analysis and dry-run output, but it must not
imply live repository mutation.

## 4. Real GitHub Boundary

Real GitHub behavior is out of scope for Sprint 7.0 and Sprint 7.1. Future real
GitHub access, if ever approved, must be explicit, allowlisted, policy-gated,
operator-approved, audited, and separate from the default demo path.

## 5. Fake LLM Boundary

Future default proposal behavior should be deterministic and fake. Fake proposal
providers should let tests prove validation, policy rejection, approval routing,
and dry-run behavior without a network call or provider credential.

## 6. Real LLM Boundary

Sprint 7.0 and Sprint 7.1 add no real LLM provider. A future provider-neutral
LLM boundary may be designed only as an optional layer. Real provider use must
not allow the model to execute tools, approve side effects, alter policy, or
select real execution mode.

## 7. Approval Requirements

Any future external side effect requires:

- normalized proposal intent
- validated arguments
- policy decision
- approval requirement calculation
- explicit operator approval
- decision binding to the exact intent
- ledger/audit evidence
- executor evidence

Without those requirements, execution must remain dry-run or rejected.

## 8. Ledger/Audit Requirements

Future runtime sprints should record:

- proposal identity
- normalized intent
- policy outcome
- approval requirement and decision
- execution mode
- dry-run or real execution result
- failure classification
- evidence timestamps and identifiers

Sprint 7.0 creates only the documentation location for this future evidence.

## 9. Secret Handling

Sprint 7.0 and Sprint 7.1 must not read secrets, print secrets, create secret
placeholders that look like real credentials, or require provider credentials.
Documentation may refer to credentials generically, but it must not include real
values.

## 10. Forbidden Actions in Sprint 7.0

Sprint 7.0 explicitly forbids:

- real GitHub writes
- real GitHub issue comments
- real label mutation
- real issue closing
- real PR mutation
- branch creation as a repository side effect
- commit creation as a repository side effect
- workflow dispatch
- token reads
- `.env` reads
- required real LLM calls
- background automation
- autonomous external side effects

The local git branch and local commit used to package this documentation sprint
are repository maintenance actions for the sprint itself, not Artifact 07
runtime capabilities.

## 11. Forbidden Actions in Sprint 7.1

Sprint 7.1 explicitly forbids:

- real GitHub reads
- real GitHub writes
- GitHub API calls
- GitHub SDKs
- real GitHub issue comments
- real label mutation
- real issue closing
- real PR mutation
- branch creation as an Artifact 07 runtime side effect
- commit creation as an Artifact 07 runtime side effect
- workflow dispatch
- token reads
- `.env` reads
- required real LLM calls
- proposal generation
- approval inbox runtime
- ledger runtime
- executor runtime
- background automation
- autonomous external side effects

## 12. Overclaim Prevention

Allowed Sprint 7.0 claim:

```text
The Sprint 7.0 documentation scaffold and safety contract are complete when
validation evidence supports that claim.
```

Allowed Sprint 7.1 claim:

```text
Sprint 7.1 local fixture loading and normalization are implemented when tests
and validation evidence support that claim.
```

Forbidden Sprint 7.0 and Sprint 7.1 claims:

- Artifact 07 is complete.
- Artifact 07 is operational.
- Artifact 07 can safely mutate repositories.
- Artifact 07 has a working GitHub client.
- Artifact 07 performs live repository reads.
- Artifact 07 has real LLM routing.
- Artifact 07 generates proposals.
- Artifact 07 has approval inbox, ledger, or executor runtime.
- Artifact 07 proves production readiness.

## 13. Green-Gate Safety Checklist

- [ ] Artifact 07 directory exists.
- [ ] Documentation scaffold is complete.
- [ ] Safety boundaries are explicit.
- [ ] Default behavior is fake/local/dry-run.
- [ ] No real GitHub write path is implemented.
- [ ] No real LLM provider is required.
- [ ] No secrets are read or printed.
- [ ] No `.env` file is tracked.
- [ ] No generated Python cache files are tracked.
- [ ] Evidence summary exists.
- [ ] Root artifact index is updated if applicable.
- [ ] Completion report avoids overclaiming.
