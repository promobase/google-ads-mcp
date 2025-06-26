"""Server wrapper for customer client link service."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.account.customer_client_link_service import (
    register_customer_client_link_tools,
    CustomerClientLinkService,
)


def register_customer_client_link_server(
    mcp: FastMCP[Any],
) -> CustomerClientLinkService:
    """Register customer client link tools with the MCP server.

    Args:
        mcp: The FastMCP server instance

    Returns:
        The CustomerClientLinkService instance for testing purposes
    """
    return register_customer_client_link_tools(mcp)
