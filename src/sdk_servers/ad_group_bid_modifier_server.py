"""Ad group bid modifier server module."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.ad_group.ad_group_bid_modifier_service import (
    register_ad_group_bid_modifier_tools,
)


def register_ad_group_bid_modifier_server(mcp: FastMCP[Any]) -> None:
    """Register ad group bid modifier server tools with the MCP server."""
    register_ad_group_bid_modifier_tools(mcp)
