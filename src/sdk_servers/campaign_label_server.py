"""Campaign label server module."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.campaign.campaign_label_service import (
    register_campaign_label_tools,
)


def register_campaign_label_server(mcp: FastMCP[Any]) -> None:
    """Register campaign label server tools with the MCP server."""
    register_campaign_label_tools(mcp)
