"""Asset group server module."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.assets.asset_group_service import register_asset_group_tools


def register_asset_group_server(mcp: FastMCP[Any]) -> None:
    """Register asset group server tools with the MCP server."""
    register_asset_group_tools(mcp)
