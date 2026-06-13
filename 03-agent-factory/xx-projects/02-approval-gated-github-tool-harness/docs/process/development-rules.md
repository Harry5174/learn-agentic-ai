# Development Rules

1. Prefer small, reviewable changes.
2. Avoid unnecessary abstractions.
3. Define contracts before implementation.
4. Write tests for important behavior.
5. Keep each module independently understandable.
6. Do not introduce advanced features before the foundation works.
7. Separate architecture planning from coding execution.
8. Do not add OAuth/JWT in V1.
9. Do not allow request body to define role/scopes.
10. Do not allow LLM to decide authorization.
11. Do not execute high-risk tools before approval.

## AI-Assisted Coding Protocol

For each sprint/module:

1. Restate objective.
2. List exact files to create or modify.
3. List tests to add.
4. Implement only that sprint/module.
5. Run tests.
6. Provide concise change summary.
7. Provide completion checklist.
8. Identify risks or deviations.

## Scope Creep Rejection Rule

When tempted to add something, ask:
“Does this help the current module’s acceptance criteria?”
If not, defer it.

## Escalate Before
- changing graph flow
- adding OAuth/JWT
- adding real GitHub write mode
- adding frontend
- replacing SQLite later
- replacing API-key identity
- adding multi-agent behavior
- changing role/scope model
- changing approval semantics
- adding a major dependency
