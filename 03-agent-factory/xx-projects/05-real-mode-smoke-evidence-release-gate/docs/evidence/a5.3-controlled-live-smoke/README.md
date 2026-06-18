# A5.3 Controlled Live Smoke Evidence

This directory holds the redacted evidence bundle for A5.3.

A5.3 demonstrated one controlled, manually approved real GitHub issue-comment
smoke execution with redacted evidence. Do not post another GitHub comment from
this evidence packet. Do not paste token values, `.env` contents,
Authorization headers, raw response headers, or unredacted transport output.

## Scope

Allowed target:

```text
Repository: Harry5174/artifact-5-github-comment-test
Issue: 1
```

Allowed fresh side-effect strategy:

```text
new_unique_body
```

The only future live action in scope remains one GitHub issue comment through
the existing Artifact 04 approval-gated real adapter path.

Live result:

```text
comment_id: 4739914610
comment_url: https://github.com/Harry5174/artifact-5-github-comment-test/issues/1#issuecomment-4739914610
```

A5.3 did not run replay/no-duplicate testing, did not run non-allowlisted live
testing, and did not perform any GitHub write besides the one issue comment.
The read-only list-comments call was used only for remote marker lookup.

## Files

- `pre-live-evidence.md` records Gate 2 checks with redacted output.
- `planned-live-flow.md` records the exact planned manual flow without secrets.
- `live-result.md` records the completed live result.
- `redaction-checks.md` records evidence-bundle redaction checks.
- `validation-results.md` records local validation commands.
- `known-limitations.md` records closeout limitations and A5.4 follow-up.
