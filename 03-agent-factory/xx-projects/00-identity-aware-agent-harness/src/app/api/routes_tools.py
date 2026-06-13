from fastapi import APIRouter

from app.api.schemas import ToolSummaryResponse, ToolsListResponse
from app.tools.registry import build_default_tool_registry

router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("", response_model=ToolsListResponse)
def list_tools() -> ToolsListResponse:
    """List public metadata for registered tools."""

    registry = build_default_tool_registry()

    tools = [
        ToolSummaryResponse(
            name=tool.name,
            description=tool.description,
            risk_level=tool.risk_level,
            required_scopes=list(tool.required_scopes),
        )
        for tool in registry.list_tools()
    ]

    return ToolsListResponse(tools=tools)