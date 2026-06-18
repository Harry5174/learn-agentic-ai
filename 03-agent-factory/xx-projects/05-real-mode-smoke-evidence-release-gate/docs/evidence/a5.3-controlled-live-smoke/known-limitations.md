# A5.3 Known Limitations

A5.3 demonstrated one controlled, manually approved real GitHub issue-comment
smoke execution with redacted evidence.

It does not prove:

- production readiness
- arbitrary repository support
- universal exactly-once execution
- CI-safe live execution
- multi-user security
- deployment readiness
- replay/no-duplicate behavior
- non-allowlisted live negative-case behavior

Known residual risks:

- remote marker deletion or editing by humans can undermine remote detection
- GitHub availability, rate limits, pagination bounds, or malformed responses
  can block execution
- redacted evidence proves the run shape, not a generalized safety guarantee
- the local A5.3 token-loading exception is test-only and not production
  behavior

Recommended next sprint:

```text
A5.4 - Replay, Negative Case, and Final Release Gate Report
```

