"""Server wrapper for reach plan service."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.planning.reach_plan_service import (
    register_reach_plan_tools,
    ReachPlanService,
)


def register_reach_plan_server(
    mcp: FastMCP[Any],
) -> ReachPlanService:
    """Register reach plan tools with the MCP server.

    Args:
        mcp: The FastMCP server instance

    Returns:
        The ReachPlanService instance for testing purposes
    """
    return register_reach_plan_tools(mcp)
