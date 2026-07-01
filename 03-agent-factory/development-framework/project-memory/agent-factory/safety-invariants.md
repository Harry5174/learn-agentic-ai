# Safety Invariants

This register defines the non-negotiable safety rules for the Agent Factory project.

---

## Universal Safety Rules

1. **No secrets printed.** Tokens, keys, and passwords must never be printed to standard output or logs.
2. **No `.env` pasted or read into LLMs.** Do not read `.env` files into AI prompts or completion reports.
3. **Fake/default first.** All tests, demos, and initial executions must use fake/mock external clients.
4. **Real mode explicit only.** Real execution must require an explicit flag (e.g., `--real`).
5. **No live external side effects without Product Owner approval.** A human must authorize the intent to write to the outside world.
6. **Approval before side effect.** The runtime must halt and require a cryptographically or durably bound approval before executing a tool.
7. **Ledger/audit evidence before completion claim.** An action is not complete until it is durably recorded.
8. **Remote idempotency marker.** Real external side effects (like GitHub comments) must include an idempotency marker to prevent duplicate writes.
9. **LLM proposes; harness decides; operator approves.** The LLM never has direct access to the execution API or tokens.
10. **Viewer cannot approve.** Read-only roles cannot issue approval decisions.
11. **Request body cannot claim identity.** Role and scopes must not be trusted from client input.
12. **Server-derived identity only.** The server determines who is taking the action.
13. **No replay or duplicate live write.** Replays are blocked unless explicitly approved/reset.

---

## Artifact-Specific Inheritance

Future artifacts inherit the safety boundaries established by past artifacts:

- **Artifact 04:** Inherits runtime real-mode safety (server-side token loading, strict repository allowlisting).
- **Artifact 05:** Inherits release-gate evidence requirements (evidence must exist before claiming success).
- **Artifact 06:** Inherits operator workbench safety (runs in fake/default mode locally without requiring live GitHub).
- **AFDF:** Inherits workflow safety (no real tokens in templates, explicit approval gates in sprints).
- **Artifact 07 (Future):** Will inherit the vertical-agent proposal boundary (LLM output must be validated before the harness accepts the proposal).
