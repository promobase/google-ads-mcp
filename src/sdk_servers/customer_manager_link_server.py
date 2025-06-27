"""Customer Manager Link server wrapper for MCP registration."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.account.customer_manager_link_service import (
    register_customer_manager_link_tools,
)


def register_customer_manager_link_server(mcp: FastMCP[Any]) -> None:
    """Register Customer Manager Link server with the MCP server."""
    register_customer_manager_link_tools(mcp)
