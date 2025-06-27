"""Server wrapper for identity verification service."""

from typing import Any

from fastmcp import FastMCP

from src.sdk_services.account.identity_verification_service import (
    register_identity_verification_tools,
    IdentityVerificationService,
)


def register_identity_verification_server(
    mcp: FastMCP[Any],
) -> IdentityVerificationService:
    """Register identity verification tools with the MCP server.

    Args:
        mcp: The FastMCP server instance

    Returns:
        The IdentityVerificationService instance for testing purposes
    """
    return register_identity_verification_tools(mcp)
