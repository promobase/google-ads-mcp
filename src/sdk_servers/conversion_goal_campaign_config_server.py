"""Conversion goal campaign config server module."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.conversions.conversion_goal_campaign_config_service import (
    register_conversion_goal_campaign_config_tools,
)


def register_conversion_goal_campaign_config_server(mcp: FastMCP[Any]) -> None:
    """Register conversion goal campaign config server tools with the MCP server."""
    register_conversion_goal_campaign_config_tools(mcp)
