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

## Artifact 07 — GitHub Repo Steward
| Evidence Item | Path | What It Proves | Verification Status |
|---------------|------|----------------|---------------------|
| Sprint 7.0-7.11 validation summaries | `xx-projects/07-github-repo-steward/docs/evidence/` | Local/fake-first repo steward layers were validated sprint-by-sprint through fixture intake, normalization, analyzer, fake proposals, policy, approval inbox, operator decisions, ledger/audit records, dry-run results, adapter boundary, real-read gate, and real-write readiness gate. | ✅ Found |
| Sprint 7.12 closeout summary | `xx-projects/07-github-repo-steward/docs/evidence/artifact-7.12-closeout-summary.md` | Artifact 07 closeout status, evidence chain, safety boundaries, limitations, and AFDF memory reconciliation. | ✅ Found |
| Artifact 07 design and safety docs | `xx-projects/07-github-repo-steward/docs/` | Final architecture, adapter boundary, real-read gate boundary, real-write readiness boundary, and non-production safety limits. | ✅ Found |

## AFDF (Phase 02.5)
| Evidence Item | Path | What It Proves | Verification Status |
|---------------|------|----------------|---------------------|
| Framework Protocols | `development-framework/docs/protocols/` | Process rules are formalized. | ✅ Found |
| Framework Templates | `development-framework/docs/templates/` | Reusable bootstraps exist. | ✅ Found |
| Template Quality Checklist | `development-framework/docs/templates/template-quality-checklist.md` | Validation standard for templates exists. | ✅ Found |

---

> **Note:** Evidence files must NEVER contain actual tokens, Authorization headers, `.env` contents, or absolute local paths.
