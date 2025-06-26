"""Campaign shared set server module."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.campaign.campaign_shared_set_service import (
    register_campaign_shared_set_tools,
)


def register_campaign_shared_set_server(mcp: FastMCP[Any]) -> None:
    """Register campaign shared set server tools with the MCP server."""
    register_campaign_shared_set_tools(mcp)
