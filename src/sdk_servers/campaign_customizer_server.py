"""Campaign Customizer server wrapper for MCP registration."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.campaign.campaign_customizer_service import (
    register_campaign_customizer_tools,
)


def register_campaign_customizer_server(mcp: FastMCP[Any]) -> None:
    """Register Campaign Customizer server with the MCP server."""
    register_campaign_customizer_tools(mcp)

