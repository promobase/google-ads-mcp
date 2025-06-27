"""Asset Group Asset server wrapper for MCP registration."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.assets.asset_group_asset_service import (
    register_asset_group_asset_tools,
)


def register_asset_group_asset_server(mcp: FastMCP[Any]) -> None:
    """Register Asset Group Asset server with the MCP server."""
    register_asset_group_asset_tools(mcp)
