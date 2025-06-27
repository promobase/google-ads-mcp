"""Product link server module."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.product_integration.product_link_service import (
    register_product_link_tools,
)


def register_product_link_server(mcp: FastMCP[Any]) -> None:
    """Register product link server tools with the MCP server."""
    register_product_link_tools(mcp)
