"""Server wrapper for customer user access service."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.account.customer_user_access_service import (
    register_customer_user_access_tools,
    CustomerUserAccessService,
)


def register_customer_user_access_server(
    mcp: FastMCP[Any],
) -> CustomerUserAccessService:
    """Register customer user access tools with the MCP server.

    Args:
        mcp: The FastMCP server instance

    Returns:
        The CustomerUserAccessService instance for testing purposes
    """
    return register_customer_user_access_tools(mcp)
