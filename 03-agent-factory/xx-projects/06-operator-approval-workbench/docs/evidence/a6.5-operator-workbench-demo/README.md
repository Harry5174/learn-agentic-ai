# A6.5 Operator Workbench Demo Evidence

## Scope

A6.5 packages the Artifact 06 local/demo operator workbench story. It is a
documentation, demo, and evidence sprint only.

This evidence folder records:

- [demo flow](demo-flow.md)
- [validation results](validation-results.md)
- [known limitations](known-limitations.md)

## Final Story

```text
AI proposes -> operator reviews -> operator approves/rejects -> harness executes safely -> status/audit/ledger evidence is visible
```

The packaged demo remains fake/default and local/demo. No GitHub token, `.env`,
or live GitHub call is required.

## Files Added

```text
docs/demos/operator-workbench-demo.md
docs/demos/portfolio-story.md
docs/evidence/a6.5-operator-workbench-demo/README.md
docs/evidence/a6.5-operator-workbench-demo/demo-flow.md
docs/evidence/a6.5-operator-workbench-demo/validation-results.md
docs/evidence/a6.5-operator-workbench-demo/known-limitations.md
```

## Runtime Boundary

A6.5 does not change `src/app`, tests, dependencies, approval semantics,
operator route behavior, static UI behavior, token handling, `.env` handling,
or GitHub execution behavior.

## Screenshot Status

No screenshots are included by default.

Future screenshots should be approved separately and checked for real tokens,
`.env` contents, authorization headers, absolute local filesystem paths, unsafe
repository data, and any other unredacted secrets.
