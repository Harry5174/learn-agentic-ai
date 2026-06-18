import pytest

from app.github.remote_marker import (
    RemoteMarkerMatchStatus,
    build_remote_idempotency_marker,
    find_remote_idempotency_markers,
    marker_body_contains_exact_match,
)


SIDE_EFFECT_ID = "side-effect-123"
ARGUMENT_HASH = "args-hash-456"


def test_marker_builds_deterministically() -> None:
    first = build_remote_idempotency_marker(
        side_effect_id=SIDE_EFFECT_ID,
        validated_arguments_hash=ARGUMENT_HASH,
    )
    second = build_remote_idempotency_marker(
        side_effect_id=SIDE_EFFECT_ID,
        validated_arguments_hash=ARGUMENT_HASH,
    )

    assert first == second
    assert first == (
        "<!-- agent_factory:v1 side_effect_id=side-effect-123 "
        "args_hash=args-hash-456 -->"
    )


@pytest.mark.parametrize("value", ["", "   "])
def test_marker_rejects_empty_side_effect_id(value: str) -> None:
    with pytest.raises(ValueError):
        build_remote_idempotency_marker(
            side_effect_id=value,
            validated_arguments_hash=ARGUMENT_HASH,
        )


@pytest.mark.parametrize("value", ["", "   "])
def test_marker_rejects_empty_arguments_hash(value: str) -> None:
    with pytest.raises(ValueError):
        build_remote_idempotency_marker(
            side_effect_id=SIDE_EFFECT_ID,
            validated_arguments_hash=value,
        )


def test_marker_is_found_inside_normal_markdown_body() -> None:
    marker = build_remote_idempotency_marker(
        side_effect_id=SIDE_EFFECT_ID,
        validated_arguments_hash=ARGUMENT_HASH,
    )
    body = f"Review note.\n\n{marker}\n\nVisible comment content."

    assert marker_body_contains_exact_match(
        body,
        side_effect_id=SIDE_EFFECT_ID,
        validated_arguments_hash=ARGUMENT_HASH,
    )


def test_parser_distinguishes_exact_match() -> None:
    marker = build_remote_idempotency_marker(
        side_effect_id=SIDE_EFFECT_ID,
        validated_arguments_hash=ARGUMENT_HASH,
    )

    matches = find_remote_idempotency_markers(
        marker,
        side_effect_id=SIDE_EFFECT_ID,
        validated_arguments_hash=ARGUMENT_HASH,
    )

    assert [match.status for match in matches] == [RemoteMarkerMatchStatus.EXACT]


def test_parser_distinguishes_wrong_side_effect_id() -> None:
    marker = build_remote_idempotency_marker(
        side_effect_id="other-side-effect",
        validated_arguments_hash=ARGUMENT_HASH,
    )

    matches = find_remote_idempotency_markers(
        marker,
        side_effect_id=SIDE_EFFECT_ID,
        validated_arguments_hash=ARGUMENT_HASH,
    )

    assert [match.status for match in matches] == [
        RemoteMarkerMatchStatus.WRONG_SIDE_EFFECT_ID
    ]


def test_parser_distinguishes_wrong_arguments_hash() -> None:
    marker = build_remote_idempotency_marker(
        side_effect_id=SIDE_EFFECT_ID,
        validated_arguments_hash="wrong-hash",
    )

    matches = find_remote_idempotency_markers(
        marker,
        side_effect_id=SIDE_EFFECT_ID,
        validated_arguments_hash=ARGUMENT_HASH,
    )

    assert [match.status for match in matches] == [
        RemoteMarkerMatchStatus.WRONG_ARGUMENTS_HASH
    ]


def test_unrelated_malformed_marker_is_ignored_safely() -> None:
    body = "<!-- agent_factory:v1 args_hash=some-other-hash -->"

    matches = find_remote_idempotency_markers(
        body,
        side_effect_id=SIDE_EFFECT_ID,
        validated_arguments_hash=ARGUMENT_HASH,
    )

    assert [match.status for match in matches] == [
        RemoteMarkerMatchStatus.MALFORMED_UNRELATED
    ]


def test_relevant_malformed_marker_fails_closed_signal() -> None:
    body = f"<!-- agent_factory:v1 side_effect_id={SIDE_EFFECT_ID} -->"

    matches = find_remote_idempotency_markers(
        body,
        side_effect_id=SIDE_EFFECT_ID,
        validated_arguments_hash=ARGUMENT_HASH,
    )

    assert [match.status for match in matches] == [
        RemoteMarkerMatchStatus.MALFORMED_RELEVANT
    ]
