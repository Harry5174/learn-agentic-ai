# A5.4 Known Limitations

A5.4 closes the Artifact 05 release-gate evidence packet, but it does not turn
the project into a broader GitHub automation system.

## Not Proven

Artifact 05 does not prove:

```text
production readiness
arbitrary repository support
universal exactly-once execution
CI live GitHub execution safety
multi-user security
deployment readiness
OAuth security
general GitHub automation
```

Those phrases are explicit non-goals and limitations, not claims.

## Replay Boundary

A5.4 used offline/mocked/spy replay proof. Real replay against GitHub was not
run.

Residual replay risks remain:

- remote marker text can be deleted or edited by humans
- GitHub listing can fail, be incomplete, or hit rate limits
- malformed, duplicated, or ambiguous markers must fail closed
- remote marker detection reduces duplicate-post risk only for the scoped path

## Live Boundary

A5.3 posted exactly one approved issue comment. A5.4 did not post a second
comment and did not perform any GitHub operation.

Future live work, if any, requires a new explicit Product Owner approval and a
new release-gate review.
