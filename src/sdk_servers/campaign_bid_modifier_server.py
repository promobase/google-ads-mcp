"""Campaign bid modifier server module."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.campaign.campaign_bid_modifier_service import (
    register_campaign_bid_modifier_tools,
)


def register_campaign_bid_modifier_server(mcp: FastMCP[Any]) -> None:
    """Register campaign bid modifier server tools with the MCP server."""
    register_campaign_bid_modifier_tools(mcp)
