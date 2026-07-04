from __future__ import annotations

from copy import deepcopy

from github_repo_steward import (
    RealReadRequest,
    build_real_read_evidence_record,
    evaluate_fake_default_real_read_gate,
    evaluate_real_read_request,
)


def test_gate_evaluation_ids_are_deterministic() -> None:
    request = _request()

    first = evaluate_real_read_request(request)
    second = evaluate_real_read_request(request)

    assert second == first
    assert first.evaluation_id == (
        "a7g:real_read_requested:fixture-owner/fixture-repo:"
        "po-read-only-preflight"
    )


def test_gate_evidence_ids_are_deterministic() -> None:
    evaluation = evaluate_fake_default_real_read_gate()

    first = build_real_read_evidence_record(
        evaluation,
        adapter_boundary_status="adapter_used",
        raw_payload_status="local_fixture_payload",
        canonical_snapshot_status="mapped_locally",
        normalization_status="normalized_locally",
        pipeline_status="local_pipeline_completed",
        summary="Fake/default adapter path only.",
    )
    second = build_real_read_evidence_record(
        evaluation,
        adapter_boundary_status="adapter_used",
        raw_payload_status="local_fixture_payload",
        canonical_snapshot_status="mapped_locally",
        normalization_status="normalized_locally",
        pipeline_status="local_pipeline_completed",
        summary="Fake/default adapter path only.",
    )

    assert second == first
    assert first.evidence_id.startswith(
        "a7v:a7g:fake_default:local/fake-default:"
    )


def test_gate_does_not_mutate_request_objects() -> None:
    request = _request()
    before = deepcopy(request)

    evaluate_real_read_request(request)

    assert request == before


def test_gate_does_not_mutate_evaluation_objects() -> None:
    evaluation = evaluate_fake_default_real_read_gate()
    before = deepcopy(evaluation)

    build_real_read_evidence_record(
        evaluation,
        adapter_boundary_status="adapter_used",
        raw_payload_status="local_fixture_payload",
        canonical_snapshot_status="mapped_locally",
        normalization_status="normalized_locally",
        pipeline_status="local_pipeline_completed",
    )

    assert evaluation == before


def _request() -> RealReadRequest:
    return RealReadRequest(
        mode="real_read_requested",
        repository_full_name="fixture-owner/fixture-repo",
        requested_by="local-operator",
        product_owner_authorized=True,
        authorization_reference="po-read-only-preflight",
        credential_source="server_side_environment_reference",
        adapter_required=True,
        write_operations_allowed=False,
        network_access_requested=True,
        evidence_expected=("read-only-payload-shape",),
    )
