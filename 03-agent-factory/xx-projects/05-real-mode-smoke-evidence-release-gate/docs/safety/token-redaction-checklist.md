# Token Redaction Checklist

Use this checklist before accepting any future A5.x evidence bundle.

Safety documentation intentionally names detection patterns so operators know
what to search for. Redaction proof should target generated evidence/log
directories, not this checklist, unless the result is clearly labeled as an
intentional documentation match.

## Hard Rules

- Do not read `.env` contents.
- Do not print `.env` contents.
- Do not paste token values into prompts, docs, logs, evidence, tests, audit
  rows, exception messages, screenshots, or shell history.
- Do not accept tokens from request bodies, model output, tool arguments, or
  approval payloads.
- Load the token server-side only.
- Use a minimum-scope fine-grained PAT only.

## Must Never Be Captured

Never capture:

- token values
- Authorization header values
- `.env` contents
- shell commands that echo or print tokens
- raw response headers
- raw unredacted transport exceptions
- screenshots containing credentials
- audit rows containing secret material
- request/model/tool payloads that attempt to provide credentials

Reject the evidence packet if any of those appear.

## May Be Captured

Safe evidence may include:

- token presence as `[TOKEN PRESENT: YES/NO]`
- token value as `[TOKEN VALUE: REDACTED]`
- `.env` ignored/untracked proof without contents
- token scope checklist status
- command names that were run without secret output
- redacted audit event names and ids
- redacted side-effect ids, argument hashes, marker placeholders, and ledger
  statuses

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

Expected result:

```text
git ls-files .env: no output
git status --short -- .env: no output
git check-ignore -v .env: shows an ignore rule, or operator records the
  repository-specific ignore explanation without printing file contents
```

## Recording Token Presence Safely

Use this format only:

```text
Token present: [TOKEN PRESENT: YES/NO]
Token value: [TOKEN VALUE: REDACTED]
Token source: server-side environment only
Token scope confirmed: yes/no
```

Do not record token prefixes, suffixes, first characters, last characters,
length, hash, checksum, screenshot, or command output containing the value.

## Redacting Command Output

Before copying command output into an evidence bundle:

- replace token values with `[TOKEN VALUE: REDACTED]`
- replace external comment URLs with `[COMMENT URL]` until A5.3 live evidence
  is explicitly approved
- replace side-effect ids with `[SIDE_EFFECT_ID]`
- replace validated argument hashes with `[ARGS_HASH]`
- replace remote markers with `[REMOTE MARKER]`
- omit raw exception messages if they could include headers, URLs with
  credentials, or environment values
- record only event names and safe ids for audit output

## Evidence Redaction Proof

The evidence bundle must include either:

```text
redaction test output
```

or:

```text
grep output proving no token-like values appear in docs/evidence/logs
```

Run grep proof against generated evidence/log directories only. If A5.1 has no
generated evidence/log directory, state that clearly and use documentation
review plus targeted repository greps as the validation evidence.

Suggested future evidence-directory checks:

```bash
git grep -n "ghp_" -- docs/evidence docs/logs || true
git grep -n "github_pat_" -- docs/evidence docs/logs || true
git grep -n "Authorization: Bearer" -- docs/evidence docs/logs || true
git grep -n "GITHUB_ACCESS_TOKEN=" -- docs/evidence docs/logs || true
git grep -n "Bearer " -- docs/evidence docs/logs || true
```

Expected result for generated evidence/log directories:

```text
no matches
```

Targeted Artifact 05 documentation scans may intentionally match this safety
checklist because it documents the detection strings:

```bash
git grep -n "ghp_" -- 03-agent-factory/xx-projects/05-real-mode-smoke-evidence-release-gate || true
git grep -n "github_pat_" -- 03-agent-factory/xx-projects/05-real-mode-smoke-evidence-release-gate || true
git grep -n "Authorization: Bearer" -- 03-agent-factory/xx-projects/05-real-mode-smoke-evidence-release-gate || true
git grep -n "GITHUB_ACCESS_TOKEN=" -- 03-agent-factory/xx-projects/05-real-mode-smoke-evidence-release-gate || true
git grep -n "Bearer " -- 03-agent-factory/xx-projects/05-real-mode-smoke-evidence-release-gate || true
```

Label any matches in this checklist as intentional documentation references.

## If Grep Finds A Possible Secret

Stop and do not accept the evidence packet.

Required response:

- remove the secret-bearing artifact from the evidence packet
- preserve only a redacted incident note
- rotate the credential if a real token may have been exposed
- check that `.env` remains untracked
- rerun redaction proof against the corrected generated evidence/log directory
- record the failure and remediation in known limitations

## Reject Evidence If

- `.env` contents appear
- token-like values appear
- Authorization headers appear
- raw response headers appear
- raw transport exceptions appear without redaction
- a token source is request/model/tool controlled
- `.env` is tracked or staged
- a live run happened without explicit Product Owner approval for that sprint
