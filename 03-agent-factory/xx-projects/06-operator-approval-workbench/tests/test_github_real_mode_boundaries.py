import json

import pytest
from pydantic import ValidationError

from app.github.fake_client import FakeGitHubIssueCommentClient
from app.github.real_client import DisabledRealGitHubIssueCommentClient
from app.github.real_mode import GitHubRealModeConfig
from app.github.schemas import GitHubIssueCommentFailure, GitHubIssueCommentRequest
from app.github.token_provider import (
    EnvironmentGitHubTokenProvider,
    MissingGitHubTokenError,
)
from app.identity.config import ADMIN_API_KEY
from app.identity.resolver import resolve_identity_from_api_key
from app.identity.schemas import IdentityContext
from app.proposer.fake import FakeProposer, FakeProposalScenario
from app.skills.argument_schemas import ArgumentValidationStatus
from app.skills.registry import build_default_skill_registry
from app.skills.schemas import (
    ProposalValidationReason,
    ProposalValidationStatus,
    SkillProposal,
    SkillProposalStep,
)
from app.skills.validator import ProposalValidator
from app.skill_graph.service import SkillGraphService
from app.state.schemas import TaskStatus
from app.tools.github_comment import GITHUB_COMMENT_TOOL_NAME


def _admin() -> IdentityContext:
    return resolve_identity_from_api_key(ADMIN_API_KEY)


def _request() -> GitHubIssueCommentRequest:
    return GitHubIssueCommentRequest(
        repository="Harry5174/learn-agentic-ai",
        issue_number=1,
        comment_body="A deterministic fake comment.",
    )


def _valid_arguments() -> dict[str, object]:
    return {
        "repository": "Harry5174/learn-agentic-ai",
        "issue_number": 1,
        "comment_body": "A deterministic fake GitHub comment.",
    }


def _proposal(arguments: dict[str, object]) -> SkillProposal:
    skill = build_default_skill_registry().get_skill(
        GITHUB_COMMENT_TOOL_NAME,
        version="1.0",
    )
    step = skill.steps[0]

    return SkillProposal(
        proposed_skill_id=skill.skill_id,
        proposed_skill_version=skill.version,
        rationale="Static GitHub real-mode boundary proposal for tests.",
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


def _default_github_comment_service() -> SkillGraphService:
    return SkillGraphService(
        proposer=FakeProposer(FakeProposalScenario.VALID_GITHUB_COMMENT),
    )


def _approved_default_run() -> dict:
    service = _default_github_comment_service()
    paused = service.start_run(
        task="Post a local/demo fake GitHub issue comment.",
        identity=_admin(),
    )
    return service.approve_run(
        run_id=paused["run_id"],
        approver=_admin(),
        reason="Approved local/demo fake GitHub comment.",
    )


def test_fake_client_remains_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AGENT_FACTORY_GITHUB_TOKEN", raising=False)

    approved = _approved_default_run()
    result = approved["tool_results"][0]

    assert approved["status"] == TaskStatus.COMPLETED
    assert result.success is True
    assert result.dry_run is True
    assert result.result["mode"] == "fake_client"
    assert result.result["client_called"] is True


def test_real_mode_is_disabled_by_default() -> None:
    config = GitHubRealModeConfig()

    assert config.enabled is False
    assert config.allowed_repositories == ()
    assert config.client_mode == "disabled"


def test_token_provider_reads_server_side_env_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AGENT_FACTORY_GITHUB_TOKEN", "secret-token-123")
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_should_not_leak")

    provider = EnvironmentGitHubTokenProvider()

    assert provider.get_token() == "secret-token-123"


@pytest.mark.parametrize("value", [None, "", "   "])
def test_missing_token_fails_closed(value: str | None) -> None:
    environ = {}
    if value is not None:
        environ["AGENT_FACTORY_GITHUB_TOKEN"] = value

    provider = EnvironmentGitHubTokenProvider(environ=environ)

    with pytest.raises(MissingGitHubTokenError) as exc_info:
        provider.get_token()

    assert str(exc_info.value) == "GitHub token is not configured."


def test_token_value_not_in_failure_message() -> None:
    provider = EnvironmentGitHubTokenProvider(
        environ={
            "AGENT_FACTORY_GITHUB_TOKEN": " ",
            "IGNORED_SECRET": "github_pat_should_not_leak",
        }
    )
    client = DisabledRealGitHubIssueCommentClient(
        config=GitHubRealModeConfig(enabled=True),
        token_provider=provider,
    )

    failure = client.post_issue_comment(_request())

    assert isinstance(failure, GitHubIssueCommentFailure)
    assert failure.message == "GitHub credentials are unavailable."
    assert "github_pat_should_not_leak" not in failure.message


def test_token_value_not_in_audit_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AGENT_FACTORY_GITHUB_TOKEN", "ghp_should_not_leak")

    approved = _approved_default_run()
    audit_payload = json.dumps(
        [event.model_dump(mode="json") for event in approved["audit_trail"]],
        sort_keys=True,
    )

    assert "ghp_should_not_leak" not in audit_payload


def test_token_value_not_in_result_object(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENT_FACTORY_GITHUB_TOKEN", "github_pat_should_not_leak")

    approved = _approved_default_run()
    result_payload = approved["tool_results"][0].model_dump_json()

    assert "github_pat_should_not_leak" not in result_payload


def test_real_mode_settings_repr_does_not_include_token() -> None:
    config = GitHubRealModeConfig(
        enabled=True,
        allowed_repositories=("Harry5174/learn-agentic-ai",),
        token_env_var="secret-token-123",
    )
    provider = EnvironmentGitHubTokenProvider(
        env_var="AGENT_FACTORY_GITHUB_TOKEN",
        environ={"AGENT_FACTORY_GITHUB_TOKEN": "secret-token-123"},
    )

    assert "secret-token-123" not in repr(config)
    assert "secret-token-123" not in str(config)
    assert "secret-token-123" not in repr(provider)


def test_request_body_cannot_enable_real_mode() -> None:
    with pytest.raises(ValidationError):
        GitHubIssueCommentRequest(
            repository="Harry5174/learn-agentic-ai",
            issue_number=1,
            comment_body="A deterministic fake comment.",
            real_mode=True,
        )

    with pytest.raises(ValidationError):
        GitHubIssueCommentRequest(
            repository="Harry5174/learn-agentic-ai",
            issue_number=1,
            comment_body="A deterministic fake comment.",
            token="ghp_should_not_leak",
        )


@pytest.mark.parametrize(
    "argument_name",
    ["real_mode", "github_token", "token", "authorization", "headers", "api_base_url"],
)
def test_model_arguments_cannot_include_token_or_real_mode(
    argument_name: str,
) -> None:
    result = ProposalValidator(build_default_skill_registry()).validate(
        proposal=_proposal({**_valid_arguments(), argument_name: "secret-token-123"}),
        identity=_admin(),
    )

    assert result.status == ProposalValidationStatus.REJECTED
    assert result.rejection_reasons == [ProposalValidationReason.INVALID_ARGUMENTS]
    assert result.validated_skill_plan is not None
    assert result.validated_skill_plan.status == ArgumentValidationStatus.REJECTED
    assert {
        issue.reason_code for issue in result.validated_skill_plan.issues
    } == {"forbidden_argument_name"}


def test_no_network_call_required_for_automated_tests(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("AGENT_FACTORY_GITHUB_TOKEN", raising=False)

    fake_result = FakeGitHubIssueCommentClient().post_issue_comment(_request())
    disabled_result = DisabledRealGitHubIssueCommentClient().post_issue_comment(
        _request()
    )

    assert fake_result.dry_run is True
    assert isinstance(disabled_result, GitHubIssueCommentFailure)
    assert disabled_result.error_type == "real_github_execution_disabled"


def test_real_client_not_wired_into_graph_execution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AGENT_FACTORY_GITHUB_TOKEN", "ghp_should_not_leak")

    approved = _approved_default_run()
    result = approved["tool_results"][0]

    assert approved["status"] == TaskStatus.COMPLETED
    assert result.result["mode"] == "fake_client"
    assert "error_type" not in result.result
