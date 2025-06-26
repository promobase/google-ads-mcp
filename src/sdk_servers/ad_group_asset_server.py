"""Ad group asset server module."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.ad_group.ad_group_asset_service import (
    register_ad_group_asset_tools,
)


def register_ad_group_asset_server(mcp: FastMCP[Any]) -> None:
    """Register ad group asset server tools with the MCP server."""
    register_ad_group_asset_tools(mcp)
