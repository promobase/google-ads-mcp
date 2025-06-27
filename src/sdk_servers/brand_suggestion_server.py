"""Brand suggestion server module."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.planning.brand_suggestion_service import (
    register_brand_suggestion_tools,
)


def register_brand_suggestion_server(mcp: FastMCP[Any]) -> None:
    """Register brand suggestion server tools with the MCP server."""
    register_brand_suggestion_tools(mcp)
