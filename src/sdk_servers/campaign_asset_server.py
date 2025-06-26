"""Campaign asset server module."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.campaign.campaign_asset_service import (
    register_campaign_asset_tools,
)


def register_campaign_asset_server(mcp: FastMCP[Any]) -> None:
    """Register campaign asset server tools with the MCP server."""
    register_campaign_asset_tools(mcp)
