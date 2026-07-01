# Evidence Index

This index points to the concrete evidence packages that prove the project's claims.

---

## Artifact 04 — Real-Mode GitHub Comment Adapter
| Evidence Item | Path | What It Proves | Verification Status |
|---------------|------|----------------|---------------------|
| Real-mode adapter code | `xx-projects/04-approval-gated-real-github-comment-adapter/src/app/side_effects/` | Runtime exists to make live comments. | ✅ Found |
| Artifact 4 audit/ledger | `xx-projects/04-approval-gated-real-github-comment-adapter/docs/audit/` | Audit logs for local A4 testing. | ⚠️ Not found during AFDF.2 inspection |

## Artifact 05 — Real-Mode Smoke Evidence Release Gate
| Evidence Item | Path | What It Proves | Verification Status |
|---------------|------|----------------|---------------------|
| A5 Spec | `xx-projects/05-real-mode-smoke-evidence-release-gate/docs/specs/artifact-5-real-mode-smoke-evidence-release-gate.md` | Formal definition of release gate requirements. | ✅ Found |
| Token Redaction Checklist | `xx-projects/05-real-mode-smoke-evidence-release-gate/docs/safety/token-redaction-checklist.md` | Redaction process was defined for evidence. | ✅ Found |
| Live Smoke Threat Model | `xx-projects/05-real-mode-smoke-evidence-release-gate/docs/safety/live-smoke-threat-model.md` | Risks of real-mode execution were mitigated. | ✅ Found |
| Live Evidence Package | `xx-projects/05-real-mode-smoke-evidence-release-gate/docs/evidence/` | Real API responses proving successful live comment execution. | ⚠️ Not found during AFDF.2 inspection |

## Artifact 06 — Operator Approval Workbench
| Evidence Item | Path | What It Proves | Verification Status |
|---------------|------|----------------|---------------------|
| Operator Workbench Demo Flow | `xx-projects/06-operator-approval-workbench/docs/evidence/a6.5-operator-workbench-demo/demo-flow.md` | Operator UI provides end-to-end approval of side effects. | ✅ Found |
| Demo Validation Results | `xx-projects/06-operator-approval-workbench/docs/evidence/a6.5-operator-workbench-demo/validation-results.md` | Demo passed safety and capability validation. | ✅ Found |
| Portfolio Story | `xx-projects/06-operator-approval-workbench/docs/demos/portfolio-story.md` | Artifact 06 is packaged for portfolio demonstration. | ✅ Found |

## AFDF (Phase 02.5)
| Evidence Item | Path | What It Proves | Verification Status |
|---------------|------|----------------|---------------------|
| Framework Protocols | `development-framework/docs/protocols/` | Process rules are formalized. | ✅ Found |
| Framework Templates | `development-framework/docs/templates/` | Reusable bootstraps exist. | ✅ Found |
| Template Quality Checklist | `development-framework/docs/templates/template-quality-checklist.md` | Validation standard for templates exists. | ✅ Found |

---

> **Note:** Evidence files must NEVER contain actual tokens, Authorization headers, `.env` contents, or absolute local paths.
