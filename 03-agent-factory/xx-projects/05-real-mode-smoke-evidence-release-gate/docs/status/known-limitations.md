# Known Limitations

This file keeps Artifact 05 honest.

## Status

A5.0 is documentation/scaffold only. It does not run live GitHub, require
credentials, read `.env`, add runtime behavior, or create a production system.

## Not Implemented

Artifact 05 does not implement:

- new GitHub adapter
- general GitHub automation
- PR creation
- branch creation
- repo file writes
- workflow dispatch
- issue creation
- labels
- milestones
- operator console
- OAuth
- MCP
- deployment
- production-ready system
- Digital FTE behavior
- arbitrary repository support
- universal exactly-once guarantee

## Operational Limits

- Fake client remains the default.
- Real mode must be explicit.
- Manual smoke must be opt-in.
- No CI live GitHub execution is allowed.
- One allowlisted repository and one allowlisted issue are allowed for a future
  manual smoke.
- One GitHub operation is in scope: post issue comment.
- Evidence must be redacted.

## No Universal Exactly-Once Guarantee

Remote marker lookup and durable reconciliation reduce duplicate-post risk for
the scoped issue-comment path. They do not prove universal exactly-once
execution.

Known residual risks include:

- remote marker deletion or editing by humans
- GitHub availability or rate limits
- bounded pagination limits
- incomplete or ambiguous remote marker lookup
- operator error during manual evidence collection

The required response to ambiguity remains fail closed.

## Evidence Limits

Redacted evidence can prove the release-gate shape, but it must not expose
tokens, Authorization headers, `.env` contents, raw unredacted transport
exceptions, or realistic-looking secrets.

