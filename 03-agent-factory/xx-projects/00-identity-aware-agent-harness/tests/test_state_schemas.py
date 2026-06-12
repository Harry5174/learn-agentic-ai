import pytest

from app.state.schemas import TaskStatus


def test_valid_task_status() -> None:
    status = TaskStatus.PAUSED_FOR_APPROVAL

    assert status == "paused_for_approval"
    assert status == TaskStatus.PAUSED_FOR_APPROVAL


def test_invalid_task_status_fails() -> None:
    with pytest.raises(ValueError):
        TaskStatus("unknown")