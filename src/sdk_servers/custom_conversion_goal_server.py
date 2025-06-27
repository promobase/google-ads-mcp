"""Custom conversion goal server module."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.conversions.custom_conversion_goal_service import (
    register_custom_conversion_goal_tools,
)


def register_custom_conversion_goal_server(mcp: FastMCP[Any]) -> None:
    """Register custom conversion goal server tools with the MCP server."""
    register_custom_conversion_goal_tools(mcp)
