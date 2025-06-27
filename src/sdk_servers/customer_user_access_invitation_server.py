"""Server wrapper for customer user access invitation service."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.account.customer_user_access_invitation_service import (
    register_customer_user_access_invitation_tools,
    CustomerUserAccessInvitationService,
)


def register_customer_user_access_invitation_server(
    mcp: FastMCP[Any],
) -> CustomerUserAccessInvitationService:
    """Register customer user access invitation tools with the MCP server.

    Args:
        mcp: The FastMCP server instance

    Returns:
        The CustomerUserAccessInvitationService instance for testing purposes
    """
    return register_customer_user_access_invitation_tools(mcp)
