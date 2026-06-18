from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_identity
from app.api.operator_schemas import (
    OperatorApprovalDetailResponse,
    OperatorApprovalListResponse,
)
from app.api.skill_routes import get_skill_run_service
from app.identity.schemas import IdentityContext
from app.operator.approval_views import (
    ApprovalInboxView,
    ApprovalViewNotFoundError,
)

router = APIRouter(prefix="/operator", tags=["operator"])


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
