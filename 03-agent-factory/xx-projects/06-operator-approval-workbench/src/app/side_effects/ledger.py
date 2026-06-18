from datetime import datetime, timezone
from typing import Any, Protocol

from app.side_effects.schemas import SideEffectRecord, SideEffectStatus


class SideEffectLedger(Protocol):
    """Minimal idempotency ledger interface for future side-effect execution."""

    def get(self, side_effect_id: str) -> SideEffectRecord | None:
        """Return a record by id, if one exists."""

    def record_started(
        self,
        *,
        side_effect_id: str,
        skill_run_id: str,
        step_id: str,
        tool_name: str,
        validated_arguments_hash: str,
    ) -> SideEffectRecord:
        """Record or return a started side-effect attempt."""

    def record_succeeded(
        self,
        side_effect_id: str,
        *,
        external_result: dict[str, Any] | None = None,
    ) -> SideEffectRecord:
        """Mark an existing side-effect attempt as succeeded."""

    def record_failed(
        self,
        side_effect_id: str,
        *,
        failure: dict[str, Any],
    ) -> SideEffectRecord:
        """Mark an existing side-effect attempt as failed."""


class InMemorySideEffectLedger:
    """Process-local idempotency ledger for tests and future dry-run wiring."""

    def __init__(self) -> None:
        self._records: dict[str, SideEffectRecord] = {}

    def get(self, side_effect_id: str) -> SideEffectRecord | None:
        return self._records.get(side_effect_id)

    def record_started(
        self,
        *,
        side_effect_id: str,
        skill_run_id: str,
        step_id: str,
        tool_name: str,
        validated_arguments_hash: str,
    ) -> SideEffectRecord:
        existing_record = self.get(side_effect_id)
        if existing_record is not None:
            return existing_record

        now = _utc_now()
        record = SideEffectRecord(
            side_effect_id=side_effect_id,
            skill_run_id=skill_run_id,
            step_id=step_id,
            tool_name=tool_name,
            validated_arguments_hash=validated_arguments_hash,
            status=SideEffectStatus.STARTED,
            created_at=now,
            updated_at=now,
        )
        self._records[side_effect_id] = record

        return record

    def record_succeeded(
        self,
        side_effect_id: str,
        *,
        external_result: dict[str, Any] | None = None,
    ) -> SideEffectRecord:
        record = self._existing_record(side_effect_id)
        updated_record = record.model_copy(
            update={
                "status": SideEffectStatus.SUCCEEDED,
                "updated_at": _utc_now(),
                "external_result": external_result,
                "failure": None,
            }
        )
        self._records[side_effect_id] = updated_record

        return updated_record

    def record_failed(
        self,
        side_effect_id: str,
        *,
        failure: dict[str, Any],
    ) -> SideEffectRecord:
        record = self._existing_record(side_effect_id)
        updated_record = record.model_copy(
            update={
                "status": SideEffectStatus.FAILED,
                "updated_at": _utc_now(),
                "failure": failure,
            }
        )
        self._records[side_effect_id] = updated_record

        return updated_record

    def has_succeeded(self, side_effect_id: str) -> bool:
        record = self.get(side_effect_id)

        return record is not None and record.status == SideEffectStatus.SUCCEEDED

    def _existing_record(self, side_effect_id: str) -> SideEffectRecord:
        record = self.get(side_effect_id)
        if record is None:
            raise KeyError(f"Unknown side effect: {side_effect_id}")

        return record


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
