import hashlib
import json
from collections.abc import Mapping

from app.skills.argument_schemas import ScalarArgumentValue


def validated_arguments_hash(
    arguments: Mapping[str, ScalarArgumentValue],
) -> str:
    """Return a stable hash for already validated scalar arguments."""

    canonical_arguments = _canonical_scalar_arguments(arguments)
    payload = json.dumps(
        canonical_arguments,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )

    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_side_effect_id(
    *,
    skill_run_id: str,
    step_id: str,
    tool_name: str,
    validated_arguments_hash: str,
) -> str:
    """Return a deterministic id for one validated side-effect attempt."""

    payload = json.dumps(
        {
            "skill_run_id": skill_run_id,
            "step_id": step_id,
            "tool_name": tool_name,
            "validated_arguments_hash": validated_arguments_hash,
        },
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )

    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _canonical_scalar_arguments(
    arguments: Mapping[str, ScalarArgumentValue],
) -> dict[str, ScalarArgumentValue]:
    if not isinstance(arguments, Mapping):
        raise TypeError("validated arguments must be a mapping")

    canonical_arguments: dict[str, ScalarArgumentValue] = {}

    for argument_name, argument_value in arguments.items():
        if not isinstance(argument_name, str):
            raise TypeError("validated argument names must be strings")

        if not isinstance(argument_value, str | int | bool):
            raise TypeError(
                "validated argument values must be string, integer, or boolean"
            )

        canonical_arguments[argument_name] = argument_value

    return canonical_arguments
