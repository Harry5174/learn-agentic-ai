from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from app.api.dependencies import (
    enforce_approval_action_rate_limit,
    get_current_identity,
)
from app.api.operator_schemas import (
    OperatorApprovalDecisionRequest,
    OperatorApprovalDecisionResponse,
    OperatorApprovalDetailResponse,
    OperatorApprovalListResponse,
)
from app.api.skill_routes import get_skill_run_service
from app.identity.schemas import IdentityContext
from app.operator.approval_actions import (
    OperatorApprovalActionConflictError,
    OperatorApprovalActionForbiddenError,
    OperatorApprovalActionNotFoundError,
    OperatorApprovalActionService,
)
from app.operator.approval_views import (
    ApprovalInboxView,
    ApprovalViewNotFoundError,
)

router = APIRouter(prefix="/operator", tags=["operator"])
WORKBENCH_STATIC_DIR = Path(__file__).resolve().parents[1] / "operator" / "static"


@router.get("/workbench", include_in_schema=False)
def get_operator_workbench() -> FileResponse:
    """Return the local/demo static operator workbench."""

    return FileResponse(
        WORKBENCH_STATIC_DIR / "workbench.html",
        media_type="text/html",
    )


@router.get("/workbench.css", include_in_schema=False)
def get_operator_workbench_css() -> FileResponse:
    """Return the local/demo workbench stylesheet."""

    return FileResponse(
        WORKBENCH_STATIC_DIR / "workbench.css",
        media_type="text/css",
    )


@router.get("/workbench.js", include_in_schema=False)
def get_operator_workbench_js() -> FileResponse:
    """Return the local/demo workbench script."""

    return FileResponse(
        WORKBENCH_STATIC_DIR / "workbench.js",
        media_type="application/javascript",
    )


@router.get("/approvals", response_model=OperatorApprovalListResponse)
def list_operator_approvals(
    identity: Annotated[IdentityContext, Depends(get_current_identity)],
) -> OperatorApprovalListResponse:
    """Return read-only local/demo approvals for the current identity."""

    del identity
    view = ApprovalInboxView(get_skill_run_service().list_runs())
    return OperatorApprovalListResponse(approvals=view.list_approvals())


@router.get(
    "/approvals/{approval_id}",
    response_model=OperatorApprovalDetailResponse,
)
def get_operator_approval(
    approval_id: str,
    identity: Annotated[IdentityContext, Depends(get_current_identity)],
) -> OperatorApprovalDetailResponse:
    """Return read-only local/demo approval detail."""

    del identity
    view = ApprovalInboxView(get_skill_run_service().list_runs())

    try:
        return view.get_approval(approval_id)
    except ApprovalViewNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found.",
        ) from exc


@router.post(
    "/approvals/{approval_id}/approve",
    response_model=OperatorApprovalDecisionResponse,
)
def approve_operator_approval(
    approval_id: str,
    identity: Annotated[
        IdentityContext,
        Depends(enforce_approval_action_rate_limit),
    ],
    request: OperatorApprovalDecisionRequest | None = None,
) -> OperatorApprovalDecisionResponse:
    """Approve a pending local/demo approval through the operator API."""

    service = OperatorApprovalActionService(get_skill_run_service())
    request = request or OperatorApprovalDecisionRequest()

    try:
        return service.approve(
            approval_id=approval_id,
            actor=identity,
            decision_reason=request.decision_reason,
            expected_side_effect_id=request.expected_side_effect_id,
            expected_args_hash=request.expected_args_hash,
        )
    except OperatorApprovalActionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found.",
        ) from exc
    except OperatorApprovalActionForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operator is not authorized to approve this approval.",
        ) from exc
    except OperatorApprovalActionConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post(
    "/approvals/{approval_id}/reject",
    response_model=OperatorApprovalDecisionResponse,
)
def reject_operator_approval(
    approval_id: str,
    identity: Annotated[
        IdentityContext,
        Depends(enforce_approval_action_rate_limit),
    ],
    request: OperatorApprovalDecisionRequest | None = None,
) -> OperatorApprovalDecisionResponse:
    """Reject a pending local/demo approval through the operator API."""

    if (
        request is None
        or request.decision_reason is None
        or not request.decision_reason.strip()
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="decision_reason is required for rejection.",
        )

    service = OperatorApprovalActionService(get_skill_run_service())

    try:
        return service.reject(
            approval_id=approval_id,
            actor=identity,
            decision_reason=request.decision_reason,
            expected_side_effect_id=request.expected_side_effect_id,
            expected_args_hash=request.expected_args_hash,
        )
    except OperatorApprovalActionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found.",
        ) from exc
    except OperatorApprovalActionForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operator is not authorized to reject this approval.",
        ) from exc
    except OperatorApprovalActionConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
