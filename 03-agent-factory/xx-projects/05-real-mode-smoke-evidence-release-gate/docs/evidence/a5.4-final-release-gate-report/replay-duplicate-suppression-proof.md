# Replay And Duplicate-Suppression Proof

## A5.4 Replay Mode

```text
A5.4 used offline/mocked/spy replay proof. Real replay against GitHub was not run.
```

Real replay was not approved. No GitHub call was made, and no second GitHub
comment was posted.

## Evidence-Backed Proof

A5.4 cites existing Artifact 04 tests. These tests use fake clients, in-memory
remote comments, local durable stores, and spy call lists. They do not require a
token and do not call GitHub.

### Marker Found Reconciles Without Posting

Reviewed test:

```text
04-approval-gated-real-github-comment-adapter/tests/test_github_real_execution_path.py::test_remote_marker_found_reconciles_and_does_not_post
```

Evidence asserted by the test:

```text
remote marker present: yes
list-comments / marker lookup path used: len(real_client.list_calls) == 1
create-comment calls: real_client.post_calls == []
remote_reconciled: true
external comment id captured from existing remote marker comment
```

### Crash-Window Remote Reconciliation Without Posting

Reviewed test:

```text
04-approval-gated-real-github-comment-adapter/tests/test_github_remote_reconciliation.py::test_crash_window_reconciles_remote_marker_without_posting
```

Evidence asserted by the test:

```text
client_called: false
remote_reconciled: true
replay_outcome: remote_reconciled
fake post client calls: []
durable ledger status: succeeded
external_result.comment_id: remote-comment-1
audit events include: remote_marker_found, remote_reconciled
```

### Fake-Client Duplicate Replay Suppresses Second Call

Reviewed test:

```text
04-approval-gated-real-github-comment-adapter/tests/test_github_comment_skill.py::test_github_comment_replay_skips_duplicate_fake_client_call_after_success
```

Evidence asserted by the test:

```text
first client_called: true
second client_called: false
second ledger_hit: true
second skipped: true
new body produces distinct side_effect_id
```

## A5.4 Conclusion

The replay/no-duplicate proof is evidence-backed by existing offline tests.
Marker-found behavior reconciles or suppresses without a create-comment call.
A5.4 did not prove this by contacting GitHub; it proved it through the existing
mocked/spy test suite.
