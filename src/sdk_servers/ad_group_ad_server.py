"""Ad group ad server module."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.ad_group.ad_group_ad_service import register_ad_group_ad_tools


def register_ad_group_ad_server(mcp: FastMCP[Any]) -> None:
    """Register ad group ad server tools with the MCP server."""
    register_ad_group_ad_tools(mcp)
