# Known Limitations

Current limitations of the Agent Factory Development Framework (AFDF).

**Last updated:** AFDF.3

---

## Framework Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Markdown-only framework | No automated enforcement of protocols or templates | Manual discipline; templates are advisory |
| AFDF memory updates are manual | AFDF | Memory can drift if a sprint forgets to update it | Make memory updates a required checklist item in the completion report |
| No CLI | No command-line tooling to validate templates or generate prompts | Use standard editor/IDE features for now |
| No validation automation | No automated checks that a completion report meets template requirements | Reviewer manually checks against template and quality checklist |
| No schema enforcement | Templates are free-form Markdown, not validated against a schema | Keep templates simple, use consistent placeholder syntax |
| No database | No persistent storage beyond Markdown files in the repository | Git provides version history |
| No multi-project synchronization | Framework is designed for the Agent Factory project only | Adapt templates if applied to other projects |
| No prompt generation | Templates are manually filled to create static bootstrap packages | AFDF.4 may address dynamic assembly |
| Templates not yet validated through real artifact usage | Used to create A07 bootstrap package in AFDF.3, but A07 has not executed yet | Refine through A07 kickoff |

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
