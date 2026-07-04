# Artifact 07 Safety Boundaries

## 1. Safety Invariants

- Use fake/local/dry-run behavior by default.
- Real mode explicit only.
- Do not read `.env`.
- Do not paste `.env`.
- Do not print secrets.
- Do not read, print, or require credentials in Sprint 7.0, Sprint 7.1, Sprint
  7.2, Sprint 7.3, Sprint 7.4, Sprint 7.5, Sprint 7.6, or Sprint 7.6R.
- Do not call GitHub APIs in Sprint 7.1, Sprint 7.2, Sprint 7.3, or Sprint
  7.4, Sprint 7.5, Sprint 7.6, or Sprint 7.6R.
- Do not perform real GitHub reads or writes in Sprint 7.1, Sprint 7.2, or
  Sprint 7.3, Sprint 7.4, Sprint 7.5, Sprint 7.6, or Sprint 7.6R.
- Do not run live external side effects.
- Do not run live external side effects without Product Owner approval.
- Treat proposal-provider output as untrusted.
- Validate and policy-check proposed actions before approval.
- Require operator approval before any future external side effect.
- Record ledger/audit evidence before claiming execution success.
- Preserve the invariant: LLM proposes; harness decides; operator approves;
  executor acts only after approval.
- Do not overclaim mocked, fake/default, local demo, unpublished, or untagged
  work as production-ready.
- Raw GitHub API responses must pass through a dedicated adapter before
  internal layers consume them.

## 2. Post-7.6 Safety Boundary

After Sprint 7.6, Artifact 07 has local fixture intake, normalization,
deterministic analysis, fake proposal drafts, local policy evaluation, pending
approval inbox items, and local operator decision records only.

- Ledger work remains future.
- Executor work remains future.
- Dry-run executor remains future.
- GitHub API adapter remains future.
- Real GitHub read/write remains future.
- Real LLM integration remains future.

Sprint 7.6R is documentation-only. It does not implement ledger runtime,
executor runtime, dry-run executor runtime, GitHub API adapter logic, real
GitHub reads, real GitHub writes, or real LLM integration.

## 3. Default-Deny Behavior

If a future proposal is ambiguous, unsafe, unsupported, outside policy, missing
evidence, or not explicitly approved, the harness should reject it or keep it in
dry-run/non-executing state. Default-deny is the expected behavior for all
unclear cases.

## 4. Fake GitHub Boundary

Sprint 7.1 adds a local fixture snapshot and normalizer only. Sprint 7.2 adds a
deterministic analyzer over that normalized local snapshot only. Sprint 7.3
adds non-executing fake proposal drafts from analyzer findings only. Sprint 7.4
adds deterministic local policy evaluation of those drafts only. Sprint 7.5
adds pending approval inbox items from policy-allowed drafts only. Sprint 7.6
adds local operator decision records for pending inbox items only. These sprints
do not add a GitHub client, GitHub SDK, GitHub API call, raw GitHub API adapter,
or real repository read path. Future fake GitHub behavior should use local
fixtures or fake adapters only. Fake behavior may support deterministic
analysis, non-executing proposal drafts, local policy evaluation, pending
approval inbox items, and local decision records, but it must not imply live
repository mutation.

## 5. Real GitHub Boundary

Real GitHub behavior is out of scope for Sprint 7.0, Sprint 7.1, Sprint 7.2,
Sprint 7.3, Sprint 7.4, Sprint 7.5, Sprint 7.6, and Sprint 7.6R. Future real
GitHub access, if ever approved, must be explicit, allowlisted, policy-gated,
operator-approved, audited, and separate from the default demo path. A future
GitHub API adapter sprint is required before raw GitHub API payloads may feed
analyzer, proposal, policy, approval, operator decision, ledger, or executor
layers.

## 6. Fake LLM Boundary

Future default proposal behavior should be deterministic and fake. Fake proposal
providers should let tests prove validation, policy rejection, approval routing,
and dry-run behavior without a network call or provider credential.

## 7. Real LLM Boundary

Sprint 7.0, Sprint 7.1, Sprint 7.2, Sprint 7.3, Sprint 7.4, Sprint 7.5, and
Sprint 7.6 add no real LLM provider. A future provider-neutral LLM boundary may
be designed only as an optional layer. Real provider use must not allow the
model to execute tools, approve side effects, reject side effects, alter policy,
or select real execution mode.

## 8. Sprint 7.3 Proposal Draft Invariants

- All Sprint 7.3 proposal objects are drafts.
- All Sprint 7.3 proposal objects require future approval.
- No Sprint 7.3 proposal object is executable.
- `requires_approval=True` does not mean an approval decision exists.
- `execution_status="draft_only"` means no execution path exists in Sprint 7.3.
- Fake proposal drafts must not claim that comments were posted, labels were
  applied, issues were closed, pull requests were changed, or any repository
  mutation occurred.

## 9. Approval Requirements

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

Sprint 7.4 policy evaluation is not approval. `allowed_for_operator_review`
means only that a local proposal draft may be routed to a future operator
review layer. Every Sprint 7.4 policy evaluation still requires future operator
approval.

Sprint 7.5 approval inbox intake is not approval. `pending_operator_review`
means only that a policy-allowed local proposal draft is waiting for a future
operator decision layer. Every Sprint 7.5 inbox item still requires future
operator approval.

Sprint 7.6 operator decision handling is not execution and is not ledger/audit
runtime. `approved_by_operator` means only that a local decision record was
created for a pending inbox item. It does not post to GitHub, enqueue executor
work, or prove a future side effect is safe to execute. `rejected_by_operator`
means only that a local rejection record was created for a pending inbox item.
It does not write a ledger entry or durable audit event.

## 10. Ledger/Audit Requirements

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

## 11. Secret Handling

Sprint 7.0, Sprint 7.1, Sprint 7.2, Sprint 7.3, Sprint 7.4, Sprint 7.5, and
Sprint 7.6 must not read secrets, print secrets, create secret placeholders
that look like real credentials, or require provider credentials. Documentation
may refer to credentials generically, but it must not include real values.

Sprint 7.4 includes local guard-pattern literals such as `GITHUB_TOKEN=`,
`Authorization:`, `Bearer `, `ghp_`, and `github_pat_` only so policy tests can
prove token-like draft text is blocked. Safety-scan hits for these strings must
be classified as intentional local guard-pattern literals, not secret values.

## 12. Forbidden Actions in Sprint 7.0

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

## 13. Forbidden Actions in Sprint 7.1

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

## 14. Forbidden Actions in Sprint 7.2

Sprint 7.2 explicitly forbids:

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
- fake proposal provider behavior
- approval inbox runtime
- ledger runtime
- executor or dry-run executor runtime
- background automation
- autonomous external side effects

The local git branch and local commit used to package this implementation
sprint are repository maintenance actions for the sprint itself, not Artifact
07 runtime capabilities.

## 15. Forbidden Actions in Sprint 7.3

Sprint 7.3 explicitly forbids:

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
- real LLM proposal generation
- policy guard runtime
- approval inbox runtime
- ledger runtime
- executor or dry-run executor runtime
- background automation
- autonomous external side effects

The local git branch and local commit used to package this implementation
sprint are repository maintenance actions for the sprint itself, not Artifact
07 runtime capabilities.

## 16. Forbidden Actions in Sprint 7.4

Sprint 7.4 explicitly forbids:

- real GitHub reads
- real GitHub writes
- GitHub API calls
- GitHub API adapter implementation
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
- real LLM proposal generation
- approval decisions
- approval inbox runtime
- ledger runtime
- executor or dry-run executor runtime
- background automation
- autonomous external side effects

The local git branch and local commit used to package this implementation
sprint are repository maintenance actions for the sprint itself, not Artifact
07 runtime capabilities.

Sprint 7.4 policy guard invariants:

- Policy guard evaluates only.
- Policy guard does not approve.
- Policy guard does not execute.
- Policy guard does not write ledger entries.
- Policy guard does not enqueue approval inbox items.
- All proposals still require future operator approval.

## 17. Forbidden Actions in Sprint 7.5

Sprint 7.5 explicitly forbids:

- real GitHub reads
- real GitHub writes
- GitHub API calls
- GitHub API adapter implementation
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
- real LLM proposal generation
- operator approval decision handling
- operator rejection handling
- ledger runtime
- executor or dry-run executor runtime
- background automation
- autonomous external side effects

The local git branch and local commit used to package this implementation
sprint are repository maintenance actions for the sprint itself, not Artifact
07 runtime capabilities.

Sprint 7.5 approval inbox invariants:

- Approval inbox stores or surfaces policy-allowed drafts only.
- Approval inbox does not approve.
- Approval inbox does not reject.
- Approval inbox does not execute.
- Approval inbox does not write ledger entries.
- Approval inbox does not call GitHub.
- All inbox items remain pending future operator review.

## 18. Forbidden Actions in Sprint 7.6

Sprint 7.6 explicitly forbids:

- real GitHub reads
- real GitHub writes
- GitHub API calls
- GitHub API adapter implementation
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
- real LLM proposal generation
- ledger runtime
- audit persistence runtime
- executor or dry-run executor runtime
- treating `approved_by_operator` as execution
- treating `rejected_by_operator` as a ledgered rejection
- background automation
- autonomous external side effects

The local git branch and local commit used to package this implementation
sprint are repository maintenance actions for the sprint itself, not Artifact
07 runtime capabilities.

Sprint 7.6 operator decision invariants:

- Operator decisions are local records only.
- Operator approval does not execute.
- Operator rejection does not execute.
- Operator decisions do not write ledger entries.
- Operator decisions do not call GitHub.
- Operator decisions do not enqueue executor work.
- All execution remains out of scope.

## 19. Forbidden Actions in Sprint 7.6R

Sprint 7.6R explicitly forbids:

- runtime source changes
- ledger runtime
- audit persistence runtime
- executor runtime
- dry-run executor runtime
- real GitHub reads
- real GitHub writes
- GitHub API calls
- GitHub API adapter implementation
- GitHub SDKs
- real GitHub issue comments
- real label mutation
- real issue closing
- real PR mutation
- workflow dispatch
- token reads
- `.env` reads
- required real LLM calls
- real LLM proposal generation
- background automation
- autonomous external side effects
- final green-gate claims by the IDE Agent

Sprint 7.6R may revise documentation and evidence interpretation only.

## 20. Overclaim Prevention

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

Allowed Sprint 7.2 claim:

```text
Sprint 7.2 local deterministic analyzer findings are implemented when tests
and validation evidence support that claim.
```

Allowed Sprint 7.3 claim:

```text
Sprint 7.3 local deterministic fake proposal drafts are implemented when tests
and validation evidence support that claim.
```

Allowed Sprint 7.4 claim:

```text
Sprint 7.4 local deterministic proposal policy evaluation is implemented when
tests and validation evidence support that claim.
```

Allowed Sprint 7.5 claim:

```text
Sprint 7.5 local approval inbox integration for policy-allowed proposal drafts
is implemented when tests and validation evidence support that claim.
```

Allowed Sprint 7.6 claim:

```text
Sprint 7.6 local operator decision handling for pending inbox items is
implemented when tests and validation evidence support that claim.
```

Allowed Sprint 7.6R claim:

```text
Sprint 7.6R formal design outline and roadmap revision is complete when
documentation validation evidence supports that claim.
```

Forbidden Sprint 7.0, Sprint 7.1, Sprint 7.2, Sprint 7.3, Sprint 7.4, Sprint
7.5, Sprint 7.6, and Sprint 7.6R claims:

- Artifact 07 is complete.
- Artifact 07 is operational.
- Artifact 07 can safely mutate repositories.
- Artifact 07 has a working GitHub client.
- Artifact 07 performs live repository reads.
- Artifact 07 has a raw GitHub API adapter.
- Artifact 07 has real LLM routing.
- Artifact 07 generates real LLM proposals.
- Artifact 07 has ledger or executor runtime.
- Artifact 07 has executable approval decisions for proposal drafts.
- Artifact 07 proves production readiness.

## 21. Green-Gate Safety Checklist

- [ ] Artifact 07 directory exists.
- [ ] Documentation scaffold is complete.
- [ ] Safety boundaries are explicit.
- [ ] Default behavior is fake/local/dry-run.
- [ ] No real GitHub write path is implemented.
- [ ] No real LLM provider is required.
- [ ] Findings remain observations, not executable proposals.
- [ ] Fake proposal drafts remain non-executing proposal objects.
- [ ] Every fake proposal draft requires future approval.
- [ ] Operator decision records remain local records only.
- [ ] Operator approvals do not execute.
- [ ] Operator rejections do not write ledger entries.
- [ ] No secrets are read or printed.
- [ ] No `.env` file is tracked.
- [ ] No generated Python cache files are tracked.
- [ ] Evidence summary exists.
- [ ] Root artifact index is updated if applicable.
- [ ] Completion report avoids overclaiming.
