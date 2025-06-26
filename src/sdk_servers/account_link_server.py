"""Server wrapper for account link service."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.account.account_link_service import (
    register_account_link_tools,
    AccountLinkService,
)


def register_account_link_server(
    mcp: FastMCP[Any],
) -> AccountLinkService:
    """Register account link tools with the MCP server.

    Args:
        mcp: The FastMCP server instance

    Returns:
        The AccountLinkService instance for testing purposes
    """
    return register_account_link_tools(mcp)
