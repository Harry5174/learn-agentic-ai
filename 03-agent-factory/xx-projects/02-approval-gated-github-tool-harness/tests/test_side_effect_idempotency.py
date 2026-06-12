import pytest

from app.side_effects.idempotency import (
    build_side_effect_id,
    validated_arguments_hash,
)


def _arguments() -> dict[str, str | int | bool]:
    return {
        "repository": "Harry5174/learn-agentic-ai",
        "issue_number": 1,
        "comment_body": "A deterministic fake comment.",
    }


def _side_effect_id(arguments: dict[str, str | int | bool] | None = None) -> str:
    argument_hash = validated_arguments_hash(arguments or _arguments())

    return build_side_effect_id(
        skill_run_id="run-123",
        step_id="post_comment",
        tool_name="github_issue_comment_boundary",
        validated_arguments_hash=argument_hash,
    )


def test_same_inputs_produce_same_validated_arguments_hash() -> None:
    first = validated_arguments_hash(_arguments())
    second = validated_arguments_hash(_arguments())

    assert first == second


def test_argument_dictionary_order_does_not_change_hash_or_side_effect_id() -> None:
    ordered = _arguments()
    reordered = {
        "comment_body": "A deterministic fake comment.",
        "issue_number": 1,
        "repository": "Harry5174/learn-agentic-ai",
    }

    assert validated_arguments_hash(ordered) == validated_arguments_hash(reordered)
    assert _side_effect_id(ordered) == _side_effect_id(reordered)


def test_argument_changes_change_validated_arguments_hash() -> None:
    baseline_hash = validated_arguments_hash(_arguments())

    assert (
        validated_arguments_hash(
            {**_arguments(), "repository": "Harry5174/other-repo"}
        )
        != baseline_hash
    )
    assert validated_arguments_hash({**_arguments(), "issue_number": 2}) != baseline_hash
    assert (
        validated_arguments_hash({**_arguments(), "comment_body": "Different."})
        != baseline_hash
    )


def test_side_effect_id_changes_when_validated_action_identity_changes() -> None:
    argument_hash = validated_arguments_hash(_arguments())
    baseline = build_side_effect_id(
        skill_run_id="run-123",
        step_id="post_comment",
        tool_name="github_issue_comment_boundary",
        validated_arguments_hash=argument_hash,
    )

    assert (
        build_side_effect_id(
            skill_run_id="run-124",
            step_id="post_comment",
            tool_name="github_issue_comment_boundary",
            validated_arguments_hash=argument_hash,
        )
        != baseline
    )
    assert (
        build_side_effect_id(
            skill_run_id="run-123",
            step_id="other_step",
            tool_name="github_issue_comment_boundary",
            validated_arguments_hash=argument_hash,
        )
        != baseline
    )
    assert (
        build_side_effect_id(
            skill_run_id="run-123",
            step_id="post_comment",
            tool_name="other_tool",
            validated_arguments_hash=argument_hash,
        )
        != baseline
    )


def test_side_effect_id_changes_when_validated_arguments_change() -> None:
    assert _side_effect_id({**_arguments(), "repository": "Harry5174/other-repo"}) != (
        _side_effect_id()
    )
    assert _side_effect_id({**_arguments(), "issue_number": 2}) != _side_effect_id()
    assert _side_effect_id({**_arguments(), "comment_body": "Different."}) != (
        _side_effect_id()
    )


def test_validated_arguments_hash_fails_closed_for_non_scalar_values() -> None:
    with pytest.raises(TypeError, match="string, integer, or boolean"):
        validated_arguments_hash(
            {
                "repository": "Harry5174/learn-agentic-ai",
                "issue_number": 1,
                "comment_body": "A deterministic fake comment.",
                "transport_config": {"timeout": 10},
            }
        )

    with pytest.raises(TypeError, match="string, integer, or boolean"):
        validated_arguments_hash(
            {
                "repository": "Harry5174/learn-agentic-ai",
                "issue_number": 1,
                "comment_body": ["not", "scalar"],
            }
        )


def test_validated_arguments_hash_requires_string_argument_names() -> None:
    with pytest.raises(TypeError, match="names must be strings"):
        validated_arguments_hash(
            {
                "repository": "Harry5174/learn-agentic-ai",
                1: "not-a-string-name",
            }
        )
