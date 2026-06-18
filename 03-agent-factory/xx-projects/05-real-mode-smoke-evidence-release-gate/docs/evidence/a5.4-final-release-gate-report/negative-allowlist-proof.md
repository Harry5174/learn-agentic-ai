# Negative Allowlist Zero-Network Proof

## A5.4 Negative Mode

Negative allowlist proof was offline and test-backed only. No non-allowlisted
live test was run, and no GitHub call was made.

## Artifact 05 Preflight Proof

Reviewed tests:

```text
05-real-mode-smoke-evidence-release-gate/tests/test_preflight_gate.py::test_non_allowlisted_repo_fails_before_network
05-real-mode-smoke-evidence-release-gate/tests/test_preflight_gate.py::test_non_allowlisted_issue_fails_before_network
05-real-mode-smoke-evidence-release-gate/tests/test_preflight_gate.py::test_network_calls_attempted_remains_zero_in_all_preflight_paths
```

Evidence asserted by the tests:

```text
non-allowlisted repository failure_reason: repository_not_allowlisted
non-allowlisted repository network_calls_attempted: 0
non-allowlisted issue failure_reason: issue_not_allowlisted
non-allowlisted issue network_calls_attempted: 0
all preflight paths network_calls_attempted: 0
```

## Artifact 04 Runtime Boundary Proof

Reviewed test:

```text
04-approval-gated-real-github-comment-adapter/tests/test_github_real_execution_adversarial.py::test_repository_allowlist_bypass_attempts_block_before_token_or_network
```

Evidence asserted by the test:

```text
error_type: repository_not_allowlisted
token_provider.calls: 0
real_client.list_calls: []
real_client.post_calls: []
```

Additional reviewed fail-closed tests block argument, side-effect id,
validated-arguments hash, missing approval binding, wrong tool binding, unsafe
remote markers, and marker lookup failures before posting.

## A5.4 Conclusion

The negative allowlist proof is evidence-backed by offline tests. The release
gate rejects non-allowlisted repository and issue cases before network, and the
runtime path blocks repository allowlist bypass attempts before token loading or
client list/create calls.
