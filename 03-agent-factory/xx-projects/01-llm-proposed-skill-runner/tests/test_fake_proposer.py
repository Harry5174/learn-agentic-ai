from app.identity.schemas import IdentityContext, Role
from app.proposer.fake import FakeProposer, FakeProposalScenario
from app.tools.schemas import RiskLevel


def _identity() -> IdentityContext:
    return IdentityContext(
        user_id="user-123",
        api_key_id="key-123",
        role=Role.OPERATOR,
        scopes=["tools:inspect"],
    )


def test_fake_proposer_returns_deterministic_low_risk_proposal() -> None:
    proposer = FakeProposer(FakeProposalScenario.VALID_LOW_RISK)

    proposal = proposer.propose("Inspect sandbox issues.", _identity())

    assert proposal.proposed_skill_id == "inspect_sandbox_health"
    assert proposal.proposed_skill_version == "1.0"
    assert proposal.steps[0].step_id == "inspect_issues"
    assert proposal.steps[0].tool_name == "inspect_sandbox_issues"
    assert proposal.steps[0].risk_level == RiskLevel.LOW
    assert proposal.steps[0].arguments == {"repository": "sandbox/demo-repo"}


def test_fake_proposer_returns_deterministic_high_risk_proposal() -> None:
    proposer = FakeProposer(FakeProposalScenario.VALID_HIGH_RISK)

    proposal = proposer.propose("Simulate workflow.", _identity())

    assert proposal.proposed_skill_id == "simulate_sandbox_workflow"
    assert proposal.proposed_skill_version == "1.0"
    assert proposal.steps[0].step_id == "simulate_workflow"
    assert proposal.steps[0].tool_name == "trigger_workflow_dry_run"
    assert proposal.steps[0].risk_level == RiskLevel.HIGH
    assert proposal.steps[0].arguments == {"workflow_name": "ci.yml", "ref": "main"}


def test_fake_proposer_can_return_invalid_proposal() -> None:
    proposer = FakeProposer(FakeProposalScenario.INVALID_PROPOSAL)

    proposal = proposer.propose("Invalid proposal.", _identity())

    assert proposal.proposed_skill_id == "inspect_sandbox_health"
    assert proposal.steps[0].step_id == "inspect_issues"
    assert proposal.steps[0].tool_name == "draft_issue_comment"


def test_fake_proposer_can_return_unknown_skill_proposal() -> None:
    proposer = FakeProposer(FakeProposalScenario.UNKNOWN_SKILL)

    proposal = proposer.propose("Unknown skill.", _identity())

    assert proposal.proposed_skill_id == "unknown_fake_skill"
    assert proposal.proposed_skill_version == "1.0"
    assert proposal.steps[0].tool_name == "inspect_sandbox_issues"
