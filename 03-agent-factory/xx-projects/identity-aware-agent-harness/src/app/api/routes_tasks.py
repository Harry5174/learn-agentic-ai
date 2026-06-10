from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_identity
from app.api.schemas import (
    ApprovalActionRequest,
    TaskAuditResponse,
    TaskCreateRequest,
    TaskSummaryResponse,
    task_summary_from_state,
)
from app.graph.service import (
    HarnessGraphService,
    TaskNotFoundError,
    TaskNotPausedError,
)
from app.identity.schemas import IdentityContext

router = APIRouter(prefix="/tasks", tags=["tasks"])

# In-memory/local service state for the Sprint 7 demo API.
# State does not survive process restart.
_task_service = HarnessGraphService()


@router.post(
    "",
    response_model=TaskSummaryResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_task(
    request: TaskCreateRequest,
    identity: Annotated[IdentityContext, Depends(get_current_identity)],
) -> TaskSummaryResponse:
    """Start a new task for the current server-derived identity."""

    state = _task_service.start_task(
        user_query=request.user_query,
        identity=identity,
    )
    return task_summary_from_state(state)


@router.get("/{task_id}", response_model=TaskSummaryResponse)
def get_task(task_id: str) -> TaskSummaryResponse:
    """Return the current public state for an existing task."""

    try:
        state = _task_service.get_task(task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        ) from exc

    return task_summary_from_state(state)


@router.post("/{task_id}/approve", response_model=TaskSummaryResponse)
def approve_task(
    task_id: str,
    identity: Annotated[IdentityContext, Depends(get_current_identity)],
    request: ApprovalActionRequest | None = None,
) -> TaskSummaryResponse:
    """Approve and resume a paused task for the current identity."""

    try:
        if request is None or request.reason is None:
            state = _task_service.approve_task(
                task_id=task_id,
                approver=identity,
            )
        else:
            state = _task_service.approve_task(
                task_id=task_id,
                approver=identity,
                reason=request.reason,
            )
    except TaskNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        ) from exc
    except TaskNotPausedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task is not paused for approval.",
        ) from exc

    return task_summary_from_state(state)


@router.post("/{task_id}/reject", response_model=TaskSummaryResponse)
def reject_task(
    task_id: str,
    identity: Annotated[IdentityContext, Depends(get_current_identity)],
    request: ApprovalActionRequest | None = None,
) -> TaskSummaryResponse:
    """Reject and resume a paused task for the current identity."""

    try:
        if request is None or request.reason is None:
            state = _task_service.reject_task(
                task_id=task_id,
                rejector=identity,
            )
        else:
            state = _task_service.reject_task(
                task_id=task_id,
                rejector=identity,
                reason=request.reason,
            )
    except TaskNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        ) from exc
    except TaskNotPausedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task is not paused for approval.",
        ) from exc

    return task_summary_from_state(state)


@router.get("/{task_id}/audit", response_model=TaskAuditResponse)
def get_task_audit(task_id: str) -> TaskAuditResponse:
    """Return the structured audit trail for an existing task."""

    try:
        audit_trail = _task_service.get_audit(task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        ) from exc

    return TaskAuditResponse(task_id=task_id, audit_trail=audit_trail)
