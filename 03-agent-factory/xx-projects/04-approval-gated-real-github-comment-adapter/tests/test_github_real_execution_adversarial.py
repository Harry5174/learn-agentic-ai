import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.audit.durable_schemas import DurableAuditEventType
from app.audit.durable_store import DurableAuditStore
from app.github.real_mode import GitHubRealModeConfig
from app.github.remote_comments import (
    RemoteIssueComment,
    RemoteIssueCommentListingError,
)
from app.github.remote_marker import build_remote_idempotency_marker
from app.github.remote_reconciliation import (
    RemoteMarkerLookupService,
    RemoteMarkerLookupStatus,
)
from app.github.schemas import (
    GitHubIssueCommentFailure,
    GitHubIssueCommentRequest,
    GitHubIssueCommentResult,
)
from app.identity.config import ADMIN_API_KEY
from app.identity.resolver import resolve_identity_from_api_key
from app.skills.argument_schemas import ArgumentValidationStatus
from app.skills.registry import build_default_skill_registry
from app.skills.schemas import (
    ProposalValidationReason,
    ProposalValidationStatus,
    SkillProposal,
    SkillProposalStep,
)
from app.skills.validator import ProposalValidator
from app.side_effects.durable_schemas import DurableSideEffectStatus
from app.side_effects.idempotency import validated_arguments_hash
from app.tools.context import ToolExecutionContext
from app.tools.github_comment import GITHUB_COMMENT_STEP_ID, GITHUB_COMMENT_TOOL_NAME
from app.tools.github_comment_real_execution import post_real_github_issue_comment
from restart_replay_helpers import (
    VALID_ARGUMENTS,
    persist_approved_action,
    persist_planned_action,
    stores,
)


REAL_REPOSITORY = "Harry5174/artifact-5-github-comment-test"
REAL_ARGUMENTS = {
    **VALID_ARGUMENTS,
    "repository": REAL_REPOSITORY,
}
SECRET_VALUES = (
    "ghp_should_not_leak",
    "github_pat_should_not_leak",
    "secret-token-123",
    "Authorization: Bearer should_not_leak",
)


class CountingTokenProvider:
    def __init__(self, token: str = "secret-token-123") -> None:
        self.token = token
        self.calls = 0

    def get_token(self) -> str:
        self.calls += 1
        return self.token


class FakeRealGitHubClient:
    def __init__(self, comments: list[RemoteIssueComment] | None = None) -> None:
        self.comments = list(comments or [])
        self.list_calls: list[GitHubIssueCommentRequest] = []
        self.post_calls: list[GitHubIssueCommentRequest] = []

    def list_issue_comments(
        self,
        request: GitHubIssueCommentRequest,
    ) -> list[RemoteIssueComment]:
        self.list_calls.append(request)
        return list(self.comments)

    def post_issue_comment(
        self,
        request: GitHubIssueCommentRequest,
    ) -> GitHubIssueCommentResult:
        self.post_calls.append(request)
        return GitHubIssueCommentResult(
            repository=request.repository,
            issue_number=request.issue_number,
            comment_id="real-comment-1",
            comment_url="https://example.invalid/real-comment-1",
            status="posted",
            dry_run=False,
        )


class FailingListClient(FakeRealGitHubClient):
    def list_issue_comments(
        self,
        request: GitHubIssueCommentRequest,
    ) -> list[RemoteIssueComment]:
        self.list_calls.append(request)
        raise RemoteIssueCommentListingError(
            "Authorization: Bearer ghp_should_not_leak"
        )


def request(arguments: dict[str, object] | None = None) -> GitHubIssueCommentRequest:
    return GitHubIssueCommentRequest.model_validate(arguments or REAL_ARGUMENTS)


def approved_context(
    tmp_path: Path,
    *,
    arguments: dict[str, object] | None = None,
    real_client: FakeRealGitHubClient | None = None,
    token_provider: CountingTokenProvider | None = None,
    allowed_repositories: tuple[str, ...] = (REAL_REPOSITORY,),
) -> tuple[ToolExecutionContext, str, str, CountingTokenProvider, FakeRealGitHubClient]:
    manager, ledger, approval_store = stores(tmp_path / "durable.sqlite")
    audit_store = DurableAuditStore(manager)
    audit_store.initialize()
    active_arguments = arguments or REAL_ARGUMENTS
    side_effect_id, args_hash = persist_approved_action(
        ledger,
        approval_store,
        arguments=active_arguments,
    )
    active_token_provider = token_provider or CountingTokenProvider()
    active_real_client = real_client or FakeRealGitHubClient()
    return (
        ToolExecutionContext(
            run_id="run-durable-1",
            step_id=GITHUB_COMMENT_STEP_ID,
            durable_side_effect_ledger=ledger,
            durable_approval_binding_store=approval_store,
            durable_audit_store=audit_store,
            real_github_issue_comment_client=active_real_client,
            github_real_mode_config=GitHubRealModeConfig(
                enabled=True,
                allowed_repositories=allowed_repositories,
                client_mode="real",
            ),
            github_token_provider=active_token_provider,
        ),
        side_effect_id,
        args_hash,
        active_token_provider,
        active_real_client,
    )


def execute(
    execution_context: ToolExecutionContext,
    *,
    side_effect_id: str,
    args_hash: str,
    active_request: GitHubIssueCommentRequest | None = None,
    tool_name: str = GITHUB_COMMENT_TOOL_NAME,
):
    return post_real_github_issue_comment(
        tool_name=tool_name,
        request=active_request or request(),
        context=execution_context,
        side_effect_id=side_effect_id,
        argument_hash=args_hash,
    )


def marker(side_effect_id: str, args_hash: str) -> str:
    return build_remote_idempotency_marker(
        side_effect_id=side_effect_id,
        validated_arguments_hash=args_hash,
    )


def remote_comment(
    body: str,
    *,
    comment_id: str = "remote-comment-1",
) -> RemoteIssueComment:
    return RemoteIssueComment(
        comment_id=comment_id,
        comment_url=f"https://example.invalid/{comment_id}",
        body=body,
    )


def audit_payload(context: ToolExecutionContext, side_effect_id: str) -> str:
    events = context.durable_audit_store.list_by_side_effect_id(side_effect_id)
    return json.dumps([event.model_dump(mode="json") for event in events])


def assert_no_secret_leak(payload: object) -> None:
    text = str(payload)
    for secret in SECRET_VALUES:
        assert secret not in text
    assert "Bearer should_not_leak" not in text


@pytest.mark.parametrize(
    "repository",
    [
        " Harry5174/artifact-5-github-comment-test",
        "Harry5174/artifact-5-github-comment-test ",
        "harry5174/artifact-5-github-comment-test",
        "Harry5174/artifact-5-github-comment-test\n",
        "https://github.com/Harry5174/artifact-5-github-comment-test",
        "Harry5174/artifact-5-github-comment-test.git",
        "Harry5174/artifact-5-github-comment-test/extra",
        "Harry5174/*",
        "Harry5174/",
    ],
)
def test_repository_allowlist_bypass_attempts_block_before_token_or_network(
    tmp_path: Path,
    repository: str,
) -> None:
    denied_arguments = {**REAL_ARGUMENTS, "repository": repository}
    execution_context, side_effect_id, args_hash, token_provider, real_client = (
        approved_context(tmp_path, arguments=denied_arguments)
    )

    result = execute(
        execution_context,
        side_effect_id=side_effect_id,
        args_hash=args_hash,
        active_request=request(denied_arguments),
    )

    assert result.success is False
    assert result.result["error_type"] == "repository_not_allowlisted"
    assert token_provider.calls == 0
    assert real_client.list_calls == []
    assert real_client.post_calls == []


def test_empty_repository_is_rejected_before_execution() -> None:
    token_provider = CountingTokenProvider()
    real_client = FakeRealGitHubClient()

    with pytest.raises(ValidationError):
        GitHubIssueCommentRequest.model_validate({**REAL_ARGUMENTS, "repository": ""})

    assert token_provider.calls == 0
    assert real_client.list_calls == []
    assert real_client.post_calls == []


def _proposal(arguments: dict[str, Any]) -> SkillProposal:
    skill = build_default_skill_registry().get_skill(
        GITHUB_COMMENT_TOOL_NAME,
        version="1.0",
    )
    step = skill.steps[0]
    return SkillProposal(
        proposed_skill_id=skill.skill_id,
        proposed_skill_version=skill.version,
        rationale="A5.4 real-mode smuggling attempt.",
        steps=[
            SkillProposalStep(
                step_id=step.step_id,
                description=step.description,
                tool_name=step.tool_name,
                allowed_args_schema=step.allowed_args_schema,
                required_scopes=step.required_scopes,
                risk_level=step.risk_level,
                arguments=arguments,
            )
        ],
    )


@pytest.mark.parametrize(
    "field_name",
    [
        "real_mode",
        "use_real_client",
        "github_token",
        "token",
        "access_token",
        "authorization",
        "headers",
        "api_base_url",
        "allowed_repositories",
        "approval_status",
        "side_effect_id",
        "validated_arguments_hash",
    ],
)
def test_request_model_control_plane_smuggling_rejected_before_execution(
    field_name: str,
) -> None:
    result = ProposalValidator(build_default_skill_registry()).validate(
        proposal=_proposal({**REAL_ARGUMENTS, field_name: "ghp_should_not_leak"}),
        identity=resolve_identity_from_api_key(ADMIN_API_KEY),
    )

    assert result.status == ProposalValidationStatus.REJECTED
    assert result.rejection_reasons == [ProposalValidationReason.INVALID_ARGUMENTS]
    assert result.validated_skill_plan is not None
    assert result.validated_skill_plan.status == ArgumentValidationStatus.REJECTED
    assert result.validated_skill_plan.step_arguments == []
    assert {
        issue.reason_code for issue in result.validated_skill_plan.issues
    }.issubset({"forbidden_argument_name", "unknown_argument"})


def test_approved_body_mutation_blocks_before_token_or_network(tmp_path: Path) -> None:
    execution_context, side_effect_id, args_hash, token_provider, real_client = (
        approved_context(tmp_path)
    )
    mutated_request = request(
        {**REAL_ARGUMENTS, "comment_body": "Mutated after approval."}
    )

    result = execute(
        execution_context,
        side_effect_id=side_effect_id,
        args_hash=args_hash,
        active_request=mutated_request,
    )

    assert result.success is False
    assert result.result["error_type"] == "local_record_mismatch"
    assert result.result["skip_reason"] == "comment_body_hash"
    assert token_provider.calls == 0
    assert real_client.list_calls == []
    assert real_client.post_calls == []


@pytest.mark.parametrize(
    "mutated_arguments",
    [
        {**REAL_ARGUMENTS, "repository": "Harry5174/alternate-allowed"},
        {**REAL_ARGUMENTS, "issue_number": 2},
    ],
)
def test_approved_repository_or_issue_mutation_blocks_before_token_or_network(
    tmp_path: Path,
    mutated_arguments: dict[str, object],
) -> None:
    execution_context, side_effect_id, args_hash, token_provider, real_client = (
        approved_context(
            tmp_path,
            allowed_repositories=(
                REAL_REPOSITORY,
                "Harry5174/alternate-allowed",
            ),
        )
    )

    result = execute(
        execution_context,
        side_effect_id=side_effect_id,
        args_hash=args_hash,
        active_request=request(mutated_arguments),
    )

    assert result.success is False
    assert result.result["error_type"] == "local_record_mismatch"
    assert token_provider.calls == 0
    assert real_client.list_calls == []
    assert real_client.post_calls == []


def test_side_effect_id_mismatch_blocks_before_token_or_network(tmp_path: Path) -> None:
    execution_context, _, args_hash, token_provider, real_client = approved_context(
        tmp_path
    )

    result = execute(
        execution_context,
        side_effect_id="other-side-effect-id",
        args_hash=args_hash,
    )

    assert result.success is False
    assert result.result["error_type"] == "side_effect_record_not_found"
    assert token_provider.calls == 0
    assert real_client.list_calls == []
    assert real_client.post_calls == []


def test_validated_arguments_hash_mismatch_blocks_before_token_or_network(
    tmp_path: Path,
) -> None:
    execution_context, side_effect_id, _, token_provider, real_client = (
        approved_context(tmp_path)
    )

    result = execute(
        execution_context,
        side_effect_id=side_effect_id,
        args_hash="wrong-hash",
    )

    assert result.success is False
    assert result.result["error_type"] == "local_record_mismatch"
    assert result.result["skip_reason"] == "validated_arguments_hash"
    assert token_provider.calls == 0
    assert real_client.list_calls == []
    assert real_client.post_calls == []


def test_missing_approval_binding_blocks_before_token_or_network(tmp_path: Path) -> None:
    manager, ledger, approval_store = stores(tmp_path / "durable.sqlite")
    audit_store = DurableAuditStore(manager)
    audit_store.initialize()
    side_effect_id = persist_planned_action(ledger, arguments=REAL_ARGUMENTS)
    with ledger.db_manager.get_connection() as conn:
        conn.execute(
            "UPDATE side_effect_records SET status = ? WHERE side_effect_id = ?",
            (DurableSideEffectStatus.APPROVED, side_effect_id),
        )
        conn.commit()
    token_provider = CountingTokenProvider()
    real_client = FakeRealGitHubClient(
        [remote_comment(marker(side_effect_id, validated_arguments_hash(REAL_ARGUMENTS)))]
    )
    execution_context = ToolExecutionContext(
        run_id="run-durable-1",
        step_id=GITHUB_COMMENT_STEP_ID,
        durable_side_effect_ledger=ledger,
        durable_approval_binding_store=approval_store,
        durable_audit_store=audit_store,
        real_github_issue_comment_client=real_client,
        github_real_mode_config=GitHubRealModeConfig(
            enabled=True,
            allowed_repositories=(REAL_REPOSITORY,),
            client_mode="real",
        ),
        github_token_provider=token_provider,
    )

    result = execute(
        execution_context,
        side_effect_id=side_effect_id,
        args_hash=validated_arguments_hash(REAL_ARGUMENTS),
    )

    assert result.success is False
    assert result.result["error_type"] == "approval_not_authorized"
    assert token_provider.calls == 0
    assert real_client.list_calls == []
    assert real_client.post_calls == []


def test_approval_binding_for_wrong_tool_blocks_before_token_or_network(
    tmp_path: Path,
) -> None:
    execution_context, side_effect_id, args_hash, token_provider, real_client = (
        approved_context(tmp_path)
    )
    with execution_context.durable_side_effect_ledger.db_manager.get_connection() as conn:
        conn.execute(
            "UPDATE approval_bindings SET tool_name = ? WHERE side_effect_id = ?",
            ("wrong_tool", side_effect_id),
        )
        conn.commit()

    result = execute(
        execution_context,
        side_effect_id=side_effect_id,
        args_hash=args_hash,
    )

    assert result.success is False
    assert result.result["error_type"] == "approval_not_authorized"
    assert token_provider.calls == 0
    assert real_client.list_calls == []
    assert real_client.post_calls == []


def test_remote_marker_with_no_local_record_does_not_reconcile_or_post(
    tmp_path: Path,
) -> None:
    manager, ledger, approval_store = stores(tmp_path / "durable.sqlite")
    audit_store = DurableAuditStore(manager)
    audit_store.initialize()
    token_provider = CountingTokenProvider()
    real_client = FakeRealGitHubClient(
        [remote_comment(marker("missing-side-effect", "missing-hash"))]
    )
    execution_context = ToolExecutionContext(
        run_id="run-durable-1",
        step_id=GITHUB_COMMENT_STEP_ID,
        durable_side_effect_ledger=ledger,
        durable_approval_binding_store=approval_store,
        durable_audit_store=audit_store,
        real_github_issue_comment_client=real_client,
        github_real_mode_config=GitHubRealModeConfig(
            enabled=True,
            allowed_repositories=(REAL_REPOSITORY,),
            client_mode="real",
        ),
        github_token_provider=token_provider,
    )

    result = execute(
        execution_context,
        side_effect_id="missing-side-effect",
        args_hash="missing-hash",
    )

    assert result.success is False
    assert result.result["error_type"] == "side_effect_record_not_found"
    assert token_provider.calls == 0
    assert real_client.list_calls == []
    assert real_client.post_calls == []


def test_planned_unapproved_record_with_remote_marker_does_not_reconcile_or_post(
    tmp_path: Path,
) -> None:
    manager, ledger, approval_store = stores(tmp_path / "durable.sqlite")
    audit_store = DurableAuditStore(manager)
    audit_store.initialize()
    side_effect_id = persist_planned_action(ledger, arguments=REAL_ARGUMENTS)
    args_hash = validated_arguments_hash(REAL_ARGUMENTS)
    token_provider = CountingTokenProvider()
    real_client = FakeRealGitHubClient([remote_comment(marker(side_effect_id, args_hash))])
    execution_context = ToolExecutionContext(
        run_id="run-durable-1",
        step_id=GITHUB_COMMENT_STEP_ID,
        durable_side_effect_ledger=ledger,
        durable_approval_binding_store=approval_store,
        durable_audit_store=audit_store,
        real_github_issue_comment_client=real_client,
        github_real_mode_config=GitHubRealModeConfig(
            enabled=True,
            allowed_repositories=(REAL_REPOSITORY,),
            client_mode="real",
        ),
        github_token_provider=token_provider,
    )

    result = execute(
        execution_context,
        side_effect_id=side_effect_id,
        args_hash=args_hash,
    )

    assert result.success is False
    assert result.result["error_type"] == "approval_not_authorized"
    assert ledger.get(side_effect_id).status == DurableSideEffectStatus.PLANNED
    assert token_provider.calls == 0
    assert real_client.list_calls == []
    assert real_client.post_calls == []


@pytest.mark.parametrize(
    ("comments", "expected_error"),
    [
        (
            [
                remote_comment("quoted\n> <!-- agent_factory:v1 side_effect_id={sid} args_hash={hash} -->")
            ],
            "marker_mismatch",
        ),
        (
            [
                remote_comment(
                    "<!-- agent_factory:v1 side_effect_id={sid} "
                    "args_hash={hash} extra=unexpected -->"
                )
            ],
            "marker_mismatch",
        ),
        (
            [
                remote_comment(
                    "<!-- agent_factory:v1 side_effect_id={sid} args_hash=wrong -->"
                )
            ],
            "marker_mismatch",
        ),
        (
            [
                remote_comment(
                    "<!-- agent_factory:v1 side_effect_id={sid} args_hash={hash} -->"
                ),
                remote_comment(
                    "<!-- agent_factory:v1 side_effect_id={sid} args_hash={hash} -->",
                    comment_id="remote-comment-2",
                ),
            ],
            "marker_ambiguous",
        ),
        (
            [
                remote_comment(
                    "<!-- agent_factory:v1 side_effect_id={sid} args_hash={hash} -->\n"
                    "<!-- agent_factory:v1 side_effect_id={sid} args_hash={hash} -->"
                )
            ],
            "marker_ambiguous",
        ),
    ],
)
def test_ambiguous_or_conflicting_remote_markers_fail_closed_with_audit(
    tmp_path: Path,
    comments: list[RemoteIssueComment],
    expected_error: str,
) -> None:
    execution_context, side_effect_id, args_hash, _, real_client = approved_context(
        tmp_path
    )
    real_client.comments = [
        RemoteIssueComment(
            comment_id=comment.comment_id,
            comment_url=comment.comment_url,
            body=comment.body.format(sid=side_effect_id, hash=args_hash),
        )
        for comment in comments
    ]

    result = execute(
        execution_context,
        side_effect_id=side_effect_id,
        args_hash=args_hash,
    )

    events = {
        event.event_type
        for event in execution_context.durable_audit_store.list_by_side_effect_id(
            side_effect_id
        )
    }

    assert result.success is False
    assert result.result["error_type"] == expected_error
    assert real_client.post_calls == []
    assert (
        DurableAuditEventType.REMOTE_MARKER_MISMATCH in events
        or DurableAuditEventType.REMOTE_MARKER_AMBIGUOUS in events
    )


def test_wrong_side_effect_id_with_same_hash_does_not_reconcile(tmp_path: Path) -> None:
    execution_context, side_effect_id, args_hash, _, real_client = approved_context(
        tmp_path
    )
    real_client.comments = [remote_comment(marker("other-side-effect", args_hash))]

    result = execute(
        execution_context,
        side_effect_id=side_effect_id,
        args_hash=args_hash,
    )

    assert result.success is True
    assert result.result["client_called"] is True
    assert result.result["remote_reconciled"] is False
    assert len(real_client.post_calls) == 1


def test_remote_listing_failure_text_is_sanitized_in_lookup_and_execution(
    tmp_path: Path,
) -> None:
    execution_context, side_effect_id, args_hash, _, real_client = approved_context(
        tmp_path,
        real_client=FailingListClient(),
    )

    lookup = RemoteMarkerLookupService(real_client).lookup(
        request=request(),
        side_effect_id=side_effect_id,
        validated_arguments_hash=args_hash,
    )
    result = execute(
        execution_context,
        side_effect_id=side_effect_id,
        args_hash=args_hash,
    )

    assert lookup.status == RemoteMarkerLookupStatus.MARKER_LOOKUP_FAILED
    assert_no_secret_leak(lookup.message)
    assert result.success is False
    assert result.result["error_type"] == "marker_lookup_failed"
    assert real_client.post_calls == []
    assert_no_secret_leak(result.model_dump_json())
    assert_no_secret_leak(audit_payload(execution_context, side_effect_id))


def test_create_comment_failure_text_and_audit_do_not_leak_secrets(
    tmp_path: Path,
) -> None:
    class SecretFailingPostClient(FakeRealGitHubClient):
        def post_issue_comment(self, request):  # noqa: ANN001, ANN201
            self.post_calls.append(request)
            return GitHubIssueCommentFailure(
                repository=request.repository,
                issue_number=request.issue_number,
                error_type="github_transport_failed",
                message="Authorization: Bearer should_not_leak",
                retryable=True,
            )

    execution_context, side_effect_id, args_hash, _, real_client = approved_context(
        tmp_path,
        real_client=SecretFailingPostClient(),
    )

    result = execute(
        execution_context,
        side_effect_id=side_effect_id,
        args_hash=args_hash,
    )

    assert result.success is False
    assert result.message == "GitHub issue-comment request failed."
    assert len(real_client.post_calls) == 1
    assert_no_secret_leak(result.model_dump_json())
    assert_no_secret_leak(audit_payload(execution_context, side_effect_id))
