"""Server wrapper for payments account service."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.account.payments_account_service import (
    register_payments_account_tools,
    PaymentsAccountService,
)


def register_payments_account_server(
    mcp: FastMCP[Any],
) -> PaymentsAccountService:
    """Register payments account tools with the MCP server.

    Args:
        mcp: The FastMCP server instance

    Returns:
        The PaymentsAccountService instance for testing purposes
    """
    return register_payments_account_tools(mcp)
