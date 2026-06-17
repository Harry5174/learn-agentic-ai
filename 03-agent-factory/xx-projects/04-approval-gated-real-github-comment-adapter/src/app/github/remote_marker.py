import re
from dataclasses import dataclass
from enum import StrEnum


MARKER_PREFIX = "agent_factory:v1"
MARKER_TEMPLATE = (
    "<!-- agent_factory:v1 side_effect_id={side_effect_id} "
    "args_hash={validated_arguments_hash} -->"
)

_AGENT_FACTORY_MARKER_RE = re.compile(
    r"<!--\s*agent_factory:v1(?P<body>.*?)-->",
    re.DOTALL,
)
_ATTRIBUTE_RE = re.compile(r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)=(?P<value>[^\s>]+)")


class RemoteMarkerMatchStatus(StrEnum):
    """Relationship between one remote marker and the target side effect."""

    EXACT = "exact"
    WRONG_SIDE_EFFECT_ID = "wrong_side_effect_id"
    WRONG_ARGUMENTS_HASH = "wrong_args_hash"
    MALFORMED_UNRELATED = "malformed_unrelated"
    MALFORMED_RELEVANT = "malformed_relevant"


@dataclass(frozen=True)
class RemoteMarkerMatch:
    """Parsed marker relationship without retaining comment body text."""

    status: RemoteMarkerMatchStatus
    side_effect_id: str | None = None
    validated_arguments_hash: str | None = None


def build_remote_idempotency_marker(
    *,
    side_effect_id: str,
    validated_arguments_hash: str,
) -> str:
    """Build the deterministic Artifact 4 remote idempotency marker."""

    normalized_side_effect_id = _required_text(
        side_effect_id,
        field_name="side_effect_id",
    )
    normalized_arguments_hash = _required_text(
        validated_arguments_hash,
        field_name="validated_arguments_hash",
    )

    return MARKER_TEMPLATE.format(
        side_effect_id=normalized_side_effect_id,
        validated_arguments_hash=normalized_arguments_hash,
    )


def find_remote_idempotency_markers(
    body: str,
    *,
    side_effect_id: str,
    validated_arguments_hash: str,
) -> list[RemoteMarkerMatch]:
    """Return all Artifact 4 marker relationships found in a comment body."""

    target_side_effect_id = _required_text(
        side_effect_id,
        field_name="side_effect_id",
    )
    target_arguments_hash = _required_text(
        validated_arguments_hash,
        field_name="validated_arguments_hash",
    )
    matches: list[RemoteMarkerMatch] = []

    for raw_match in _AGENT_FACTORY_MARKER_RE.finditer(body):
        marker_body = raw_match.group("body")
        attributes = _marker_attributes(marker_body)
        parsed_side_effect_id = attributes.get("side_effect_id")
        parsed_arguments_hash = attributes.get("args_hash")

        if parsed_side_effect_id is None:
            matches.append(
                RemoteMarkerMatch(status=RemoteMarkerMatchStatus.MALFORMED_UNRELATED)
            )
            continue

        if parsed_side_effect_id != target_side_effect_id:
            matches.append(
                RemoteMarkerMatch(
                    status=RemoteMarkerMatchStatus.WRONG_SIDE_EFFECT_ID,
                    side_effect_id=parsed_side_effect_id,
                    validated_arguments_hash=parsed_arguments_hash,
                )
            )
            continue

        if _has_unexpected_attributes(attributes) or _marker_is_quoted(
            body,
            raw_match.start(),
        ):
            matches.append(
                RemoteMarkerMatch(
                    status=RemoteMarkerMatchStatus.MALFORMED_RELEVANT,
                    side_effect_id=parsed_side_effect_id,
                    validated_arguments_hash=parsed_arguments_hash,
                )
            )
            continue

        if parsed_arguments_hash is None:
            matches.append(
                RemoteMarkerMatch(
                    status=RemoteMarkerMatchStatus.MALFORMED_RELEVANT,
                    side_effect_id=parsed_side_effect_id,
                )
            )
            continue

        if parsed_arguments_hash != target_arguments_hash:
            matches.append(
                RemoteMarkerMatch(
                    status=RemoteMarkerMatchStatus.WRONG_ARGUMENTS_HASH,
                    side_effect_id=parsed_side_effect_id,
                    validated_arguments_hash=parsed_arguments_hash,
                )
            )
            continue

        matches.append(
            RemoteMarkerMatch(
                status=RemoteMarkerMatchStatus.EXACT,
                side_effect_id=parsed_side_effect_id,
                validated_arguments_hash=parsed_arguments_hash,
            )
        )

    return matches


def marker_body_contains_exact_match(
    body: str,
    *,
    side_effect_id: str,
    validated_arguments_hash: str,
) -> bool:
    """Return whether a comment body contains the exact target marker."""

    return any(
        match.status == RemoteMarkerMatchStatus.EXACT
        for match in find_remote_idempotency_markers(
            body,
            side_effect_id=side_effect_id,
            validated_arguments_hash=validated_arguments_hash,
        )
    )


def _required_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or value.strip() == "":
        raise ValueError(f"{field_name} must be a non-empty string")

    return value.strip()


def _marker_attributes(marker_body: str) -> dict[str, str]:
    return {
        match.group("name"): match.group("value")
        for match in _ATTRIBUTE_RE.finditer(marker_body)
    }


def _has_unexpected_attributes(attributes: dict[str, str]) -> bool:
    return not set(attributes).issubset({"side_effect_id", "args_hash"})


def _marker_is_quoted(body: str, marker_start: int) -> bool:
    line_start = body.rfind("\n", 0, marker_start) + 1
    line_prefix = body[line_start:marker_start]
    return line_prefix.lstrip().startswith(">")
