from app.side_effects.idempotency import validated_arguments_hash
from restart_replay_helpers import (
    VALID_ARGUMENTS,
    context_for_identity_only,
    side_effect_id_for,
)


def test_validated_arguments_hash_and_side_effect_id_are_deterministic() -> None:
    reordered_arguments = {
        "comment_body": VALID_ARGUMENTS["comment_body"],
        "issue_number": VALID_ARGUMENTS["issue_number"],
        "repository": VALID_ARGUMENTS["repository"],
    }
    context_1 = context_for_identity_only()
    context_2 = context_for_identity_only()

    assert validated_arguments_hash(VALID_ARGUMENTS) == validated_arguments_hash(
        reordered_arguments
    )
    assert side_effect_id_for(context_1.run_id) == side_effect_id_for(
        context_2.run_id
    )
