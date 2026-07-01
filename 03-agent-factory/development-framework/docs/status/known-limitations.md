# Known Limitations

Current limitations of the Agent Factory Development Framework (AFDF).

---

## Framework Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Markdown-only framework | No automated enforcement of protocols or templates | Manual discipline; templates are advisory |
| Manual updates required | Project memory, decision logs, and status docs must be updated by hand | Include memory updates in every sprint's completion checklist |
| No CLI | No command-line tooling to validate templates or generate prompts | Use standard editor/IDE features for now |
| No validation automation | No automated checks that a completion report meets template requirements | Reviewer manually checks against template |
| No schema enforcement | Templates are free-form Markdown, not validated against a schema | Keep templates simple and self-documenting |
| No database | No persistent storage beyond Markdown files in the repository | Git provides version history |
| No multi-project synchronization | Framework is designed for the Agent Factory project only | Adapt templates if applied to other projects |

---

## Artifact Sequence Limitations

| Limitation | Impact |
|------------|--------|
| Artifacts 00–06 remain local/demo | No production deployment, no production authentication |
| No live GitHub execution in CI | CI uses fake/mock clients only |
| No arbitrary repository support | Real GitHub execution is limited to allowlisted repositories |
| No OAuth/OIDC | Identity is server-derived but not production-grade |
| No MCP integration | No Model Context Protocol support yet |
| No frontend/operator console deployment | Operator workbench runs locally only |
