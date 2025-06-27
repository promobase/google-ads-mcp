"""Customer Label server wrapper for MCP registration."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.account.customer_label_service import (
    register_customer_label_tools,
)


def register_customer_label_server(mcp: FastMCP[Any]) -> None:
    """Register Customer Label server with the MCP server."""
    register_customer_label_tools(mcp)

