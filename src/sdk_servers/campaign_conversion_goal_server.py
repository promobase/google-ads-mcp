"""Campaign Conversion Goal server wrapper for MCP registration."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.campaign.campaign_conversion_goal_service import (
    register_campaign_conversion_goal_tools,
)


def register_campaign_conversion_goal_server(mcp: FastMCP[Any]) -> None:
    """Register Campaign Conversion Goal server with the MCP server."""
    register_campaign_conversion_goal_tools(mcp)
