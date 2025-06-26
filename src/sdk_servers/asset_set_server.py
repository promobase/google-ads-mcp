"""Asset set server module."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.assets.asset_set_service import register_asset_set_tools


def register_asset_set_server(mcp: FastMCP[Any]) -> None:
    """Register asset set server tools with the MCP server."""
    register_asset_set_tools(mcp)
