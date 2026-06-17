# Token Redaction Checklist

Use this checklist before accepting any future A5.x evidence bundle.

## Hard Rules

- Do not read `.env` contents.
- Do not print `.env` contents.
- Do not paste token values into prompts, docs, logs, evidence, tests, audit
  rows, exception messages, screenshots, or shell history.
- Do not accept tokens from request bodies, model output, tool arguments, or
  approval payloads.
- Load the token server-side only.
- Use a minimum-scope fine-grained PAT only.

## Minimum Token Scope

For a future manual smoke:

- one allowlisted repository
- Issues permission: read and write
- short expiration
- no Contents permission
- no Actions/workflows permission
- no broad repo scope

## Safe `.env` Checks

These commands check ignore/tracking status only and must not print secret
contents:

```bash
git status --short -- .env
git ls-files .env
git check-ignore -v .env
```

## Evidence Redaction Proof

The evidence bundle must include either:

```text
redaction test output
```

or:

```text
grep output proving no token-like values appear in docs/evidence/logs
```

## Reject Evidence If

- `.env` contents appear
- token-like values appear
- Authorization headers appear
- raw response headers appear
- raw transport exceptions appear without redaction
- a token source is request/model/tool controlled
- `.env` is tracked or staged
- a live run happened without explicit Product Owner approval for that sprint

