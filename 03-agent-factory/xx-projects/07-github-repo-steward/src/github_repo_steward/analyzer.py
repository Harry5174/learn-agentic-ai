"""Deterministic local repository stewardship finding analyzer."""

from __future__ import annotations

from github_repo_steward.models import (
    CiStatusSummary,
    IssueRecord,
    NormalizedRepoSnapshot,
    PullRequestRecord,
    RepoFinding,
)

STALE_ISSUE_DAYS = 30


def analyze_repo_snapshot(snapshot: NormalizedRepoSnapshot) -> list[RepoFinding]:
    """Analyze a normalized local snapshot and return stable observations."""

    findings: list[RepoFinding] = []
    ci_statuses = {
        (status.target_type, status.target_number): status
        for status in snapshot.ci_statuses
    }

    for issue in snapshot.issues:
        if issue.state != "open":
            continue
        findings.extend(_analyze_issue(issue))

    for pull_request in snapshot.pull_requests:
        if pull_request.state != "open":
            continue
        findings.extend(_analyze_pull_request(pull_request, ci_statuses))

    return sorted(
        findings,
        key=lambda finding: (
            finding.target_type,
            finding.target_number,
            finding.finding_type,
        ),
    )


def _analyze_issue(issue: IssueRecord) -> list[RepoFinding]:
    findings: list[RepoFinding] = []
    labels = {label.lower() for label in issue.labels}

    if "needs-info" in labels:
        findings.append(
            _finding(
                finding_type="issue_missing_reproduction",
                severity="medium",
                target_type="issue",
                target_number=issue.number,
                title="Issue needs reproduction details",
                summary=(
                    "Open issue is labeled needs-info, indicating the local "
                    "snapshot lacks enough reproduction detail for stewardship."
                ),
                evidence=(
                    f"issue_number={issue.number}",
                    "label=needs-info",
                    f"comments_count={issue.comments_count}",
                    f"stale_days={issue.stale_days}",
                ),
            )
        )

    if issue.stale_days >= STALE_ISSUE_DAYS and issue.comments_count == 0:
        findings.append(
            _finding(
                finding_type="issue_stale_no_maintainer_response",
                severity="low",
                target_type="issue",
                target_number=issue.number,
                title="Stale issue has no recorded maintainer response",
                summary=(
                    "Open issue is stale in the normalized fixture and has no "
                    "comments, which Sprint 7.2 treats as a local proxy for no "
                    "maintainer response."
                ),
                evidence=(
                    f"issue_number={issue.number}",
                    f"stale_days={issue.stale_days}",
                    f"comments_count={issue.comments_count}",
                    f"threshold_days={STALE_ISSUE_DAYS}",
                ),
            )
        )

    return findings


def _analyze_pull_request(
    pull_request: PullRequestRecord,
    ci_statuses: dict[tuple[str, int], CiStatusSummary],
) -> list[RepoFinding]:
    findings: list[RepoFinding] = []
    ci_status = ci_statuses.get(("pull_request", pull_request.number))

    if pull_request.ci_status.lower() == "failing" or _is_failed_ci(ci_status):
        evidence = [
            f"pull_request_number={pull_request.number}",
            f"ci_status={pull_request.ci_status}",
        ]
        if ci_status is not None:
            evidence.extend(
                (
                    f"ci_summary_status={ci_status.status}",
                    f"ci_summary_conclusion={ci_status.conclusion}",
                )
            )
        findings.append(
            _finding(
                finding_type="pull_request_failing_ci",
                severity="high",
                target_type="pull_request",
                target_number=pull_request.number,
                title="Pull request has failing CI",
                summary=(
                    "Open pull request has failing CI according to the "
                    "normalized pull request record or matching CI summary."
                ),
                evidence=tuple(evidence),
            )
        )

    if pull_request.review_status == "waiting_for_review":
        findings.append(
            _finding(
                finding_type="pull_request_waiting_for_review",
                severity="medium",
                target_type="pull_request",
                target_number=pull_request.number,
                title="Pull request is waiting for review",
                summary=(
                    "Open pull request is marked waiting_for_review in the "
                    "normalized fixture."
                ),
                evidence=(
                    f"pull_request_number={pull_request.number}",
                    "review_status=waiting_for_review",
                    f"ci_status={pull_request.ci_status}",
                    f"stale_days={pull_request.stale_days}",
                ),
            )
        )

    return findings


def _is_failed_ci(ci_status: CiStatusSummary | None) -> bool:
    if ci_status is None:
        return False
    return ci_status.conclusion.lower() in {"failure", "failed"}


def _finding(
    *,
    finding_type: str,
    severity: str,
    target_type: str,
    target_number: int,
    title: str,
    summary: str,
    evidence: tuple[str, ...],
) -> RepoFinding:
    return RepoFinding(
        finding_id=f"a7:{finding_type}:{target_type}:{target_number}",
        finding_type=finding_type,
        severity=severity,
        target_type=target_type,
        target_number=target_number,
        title=title,
        summary=summary,
        evidence=evidence,
    )
